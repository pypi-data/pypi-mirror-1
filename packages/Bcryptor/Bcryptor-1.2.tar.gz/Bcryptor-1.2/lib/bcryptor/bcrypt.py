#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Bcryptor Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""The high level wrapper about bcrypt.

Manage easily the hashing and checking of passwords.
"""

__all__ = ['Bcrypt']

from . import engine


class Bcrypt(object):
    """Allow to store passwords safely and compare them.

    ...

    Parameters
    ----------
    background : boolean, optional
        If *True*, the exceptions are not raised else that they are
        logged. It is passed to `engine.Engine()`.
        Default is *False*.
    default_cost : int
        The computational expense parameter.
        Default is *10*.
    plus_admin_cost: int
        The administrator's cost added to `default_cost`.
        Default is *2*.

    Attributes
    ----------
    _engine : class instance
        The low level wrapper.
    default_cost
    plus_admin_cost

    """
    _DEFAULT_COST = 10
    _PLUS_ADMIN_COST = 2

    def __init__(self, default_cost=_DEFAULT_COST,
                 plus_admin_cost=_PLUS_ADMIN_COST, background=False):
        self._engine = engine.Engine(background)
        self.default_cost = default_cost
        self.plus_admin_cost = plus_admin_cost

    def _get_salt_schema(self, raw_hash):
        """Get the salt schema of a hash given.

        ...

        Parameters
        ----------
        raw_hash : str
            The *Bcrypt* hash schema where the salt is got.

        Returns
        -------
        The salt.

        """
        # The salt's schema length is of 29 characters.
        # From there until the end is the password hash.
        return raw_hash[:29]

    def _split_schema(self, raw_hash):
        """Split all information of a hash.

        ...

        Parameters
        ----------
        raw_hash : str
            The *bcrypt* hash schema.

        Returns
        -------
        tuple of int, int, str
            Version, cost, salt plus password hash.

        """
        # When is used `split` on the hash schema there's an empty string
        # between the start of the string and the '$' character.
        # If it didn't do that, you wouldn't be able to tell the difference
        # bewteen '$foo' and 'foo$'.
        version, cost, salt_hash = raw_hash.split('$')[1:]
        return version, cost, salt_hash

    def create(self, key, cost=None, admin=False):
        """Hash a `key` using the *bcryp* hash algorithm.

        ...

        Parameters
        ----------
        key : str
            A secret encryption key, which can be a user-chosen password
            of up to 56 bytes (including a terminating zero byte when
            the key is an ASCII string).
        cost : int, optional
            Control how expensive the key schedule is to compute.
            Default is the `default_cost` attribute.
        admin : boolean, optional
            If *True*, use a cost greater.
            Default is *False*.

        Returns
        -------
        The *bcrypt* hash schema for the `key`.

        Notes
        -----
        With higher cost becomes harder for crackers to try get
        passwords (even if your database is stolen), but it's slower
        too to check them.

        """
        # Cann't refer to 'self' in the function definition because
        # it doesn't exist yet.
        if cost is None:
            cost_ = self.default_cost
        else:
            cost_ = cost

        if admin:
            cost_ += self.plus_admin_cost

        return self._engine.hash_key(key, self._engine.generate_salt(cost_))

    def valid(self, key, raw_hash):
        """Compare a `key` against the hash schema.

        ...

        Parameters
        ----------
        key : str
            The password to compare. In the first the password is hashed
            using the same salt of the hash schema given.
        raw_hash : str
            The bcrypt hash schema.

        Returns
        -------
        boolean
            *True* if the `key` is the original password, *False* otherwise.

        """
        self._engine._check_schema(raw_hash, len_hash=True)
        salt = self._get_salt_schema(raw_hash)

        # Create the new hash using the salt of the hash schema given.
        new_hash = self._engine.hash_key(key, salt)

        if raw_hash in new_hash:
            return True

        return False
