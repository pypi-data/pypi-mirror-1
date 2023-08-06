#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Bcryptor Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""The low level wrapper about bcrypt.

It takes charge that data are correct before being sent to the C library.
"""

import random
import re

import yamlog
cimport _engine

_log = yamlog.logger(__name__)


cdef class Engine(object):
    """Python wrapper for the `bcrypt()` extension calls.

    ...

    Parameters
    ----------
    background : boolean
        If *True*, the exceptions are not raised else that they are
        logged. Useful for daemons or other background processes.

    Attributes
    ----------
    LEN_SALT : int
        The length of the salt. It's set to 128 bits (16 chars.)
    LEN_SCHEMA : int
        The length of hash schema is of 60 characters.
    SCHEMA : regular expression
        The hash schema.
    rand : class instance of `Randomizer`
        To get random strings.
    throw : class `yamlog.Throw()`
        Instance to throw exceptions which are logged.

    """
    LEN_SALT = 16  # bytes
    LEN_SCHEMA = 60

    # The hash schema.
    _BCRYPT_VERSION = '2'
    _RANGE = r'(0[4-9]|[12][0-9]|3[01])'  # 04-31 log. rounds.
    _BASE64_CODE = r'[\.\/A-Za-z0-9]+'
    SCHEMA = re.compile("^\${0}a\${1}\${2}$".format(
        _BCRYPT_VERSION, _RANGE, _BASE64_CODE))

    # Declaration for dynamic attributes
    cdef rand, throw

    def __init__(self, background):
        self.rand = Randomizer()
        self.throw = yamlog.Throw(_log, background)

    def _check_schema(self, raw_hash, len_hash=False):
        """Check both length and schema of a given hash.

        ...

        Parameters
        ----------
        raw_hash : str
            The *bcrypt* hash schema.
        len_hash : boolean, optional
            If *True*, check the length.
            Default is *False*.

        Returns
        -------
        boolean
           *True* if it's valid, *False* otherwise.

        Raises
        ------
        SaltError
            If `raw_hash`is not a *bcrypt* salt schema.
        HashError
            If the hash is not full.

        """
        if not self.SCHEMA.search(raw_hash):
            self.throw(SaltError, raw_hash, 'invalid salt schema')

        if len_hash and len(raw_hash) is not self.LEN_SCHEMA:
            self.throw(HashError, raw_hash, 'invalid hash')

        return True

    def generate_salt(self, rounds=None):
        """Generate a salt with a given computational cost.

        The salt is a random string of 128 bits (16 characters) length.

        ...

        Parameters
        ----------
        rounds : int
            The logarithm rounds called cost.

        Returns
        -------
        str
            The salt schema.

        Raises
        ------
        TypeError
            If the data type is not valid.

        """
        # Definition of C variables which are passed to the C function.
        cdef int c_log_rounds  # Logarithm rounds.
        cdef unsigned char* c_salt  # Salt.

        # Checking
        # ========
        if rounds is None:
            self.throw(TypeError, 'you must enter the rounds number')

        if not isinstance(rounds, int):
            self.throw(TypeError, rounds, 'the rounds number must be numeric')

        # Set values minimum and maximum for the round as it's in the C call.
        # The C call doesn't manage negative values neither upper than 255.
        if rounds < 4:
            rounds = 4
        elif rounds > 31:
            rounds = 31
        # ===
        c_log_rounds = rounds  # Passed from Python function.

        # Get a random salt using a length by default, and it's passed
        # to the C variable.
        salt = self.rand(self.LEN_SALT)
        c_salt = <unsigned char*> salt  # Cast the Python string.

        # Call to the C function using the C variables.
        return _engine.bcrypt_gensalt_linux(c_log_rounds, c_salt)

    def hash_key(self, key=None, salt=None):
        """Calculate a *bcrypt()* password hash.

        ...

        Parameters
        ----------
        key : str
            The text, generally a password, to be hashed.
        salt : str
            The text used to add to the hash generated.

        Returns
        -------
        str
           The *bcrypt* hash.

        Raises
        ------
        TypeError
            If the data type is not valid.

        See Also
        --------
        generate_salt

        """
        # C variables passed from arguments of Python function.
        cdef char* c_key
        cdef char* c_salt

        # Checking
        # ========
        if key is None:
            self.throw(TypeError, 'you must enter the key')

        if salt is None:
            self.throw(TypeError, 'you must enter the salt')

        if not isinstance(key, basestring):
            self.throw(TypeError, key, 'the key must be a string')

        self._check_schema(salt)
        # ===
        c_key = key
        c_salt = salt

        return _engine.bcrypt(c_key, c_salt)  # Call to C function.


cdef class Randomizer(object):
    """Generate random strings.

    Use a pseudo random number generator with sources provided by the
    operating system (such as */dev/urandom* on Unix).

    ...

    Attributes
    ----------
    prng : class instance of `random.SystemRandom`
        Initialize the *PRNG* of the operating system.

    Notes
    -----
    Each byte is randomly chosen from a domain of 256 possible values
    (range 0-255) per character, thus a greater security is obtained.

    """
    # Declaration for dynamic attributes
    cdef prng

    def __init__(self):
        self.prng = random.SystemRandom()

    def __call__(self, bytes):
        """
        ...

        Parameters
        ----------
        bytes : int
            Number of bytes, which are going to be translated to characters.

        Returns
        -------
        str
            A number (given by `bytes`) of characters.

        """
        rand = ''
        for x in range(bytes):
            rand += chr(self.prng.randrange(256))  # 0-255

        return rand


# Exceptions
# ==========

class HashError(Exception):
    pass


class SaltError(Exception):
    pass
