Bcrypt is an implementation of a modern password hashing algorithm, based on
the Blowfish block cipher, by Niels Provos and David Mazieres. It has been
the default password scheme since OpenBSD 2.1.

A paper on the algorithm that explains its design decisions is available here:
    http://www.usenix.org/events/usenix99/provos.html

The most important property of *bcrypt* is that it is adaptable to future
processor performance improvements, allowing you to arbitrarily increase the
processing cost of checking a password while still maintaining compatibility
with your older password hashes.

This package provides a high level object oriented wrapper around *bcrypt*,
as well as low level bindings to the C library. It uses the random number
generator `random.SystemRandom()` to create the salts.

Installation
------------
To build the module from source code, read documentation on *doc/source.txt*.

Logging
-------
Yamlog_ manages the error catching code and error reporting. Read its
documentation if want to be set up.

Use
---
Typical usage::

    import bcryptor

    hasher = bcryptor.Bcrypt()
    hash = hasher.create('crack my pass')

And to validate::

    >>> hasher.valid('crack my pass', hash)
    True
    >>> hasher.valid('Crack my pass', hash)
    False


.. _Yamlog: http://pypi.python.org/pypi/Yamlog
