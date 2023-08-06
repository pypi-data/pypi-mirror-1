#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import setuptools
#from Cython import Distutils

url = 'http://www.bitbucket.org/ares/bcryptor/'

# http://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = """
Development Status :: 5 - Production/Stable
Environment :: Web Environment
Environment :: Other Environment
Intended Audience :: Developers
License :: OSI Approved :: ISC License (ISCL)
Operating System :: POSIX
Operating System :: POSIX :: Linux
Programming Language :: C
Programming Language :: Python :: 2.4
Topic :: Security :: Cryptography
"""

keywords = """
bcrypt
crypto
cryptography
hash
openbsd
password
security
"""

# Build the extension module
module = setuptools.Extension(
    'bcryptor.engine',
    sources=[
        'lib/bcryptor/wrap/engine.pyx',
        'lib/bcryptor/wrap/src/blowfish.c',
    ],
)

# ============

class Get(object):
    """Get all metadata."""
    here = os.path.abspath(os.path.dirname(__file__))  # Current dir.

    def __init__(self, authors_file='AUTHORS.txt', changes_file='CHANGES.txt',
                 readme_file='README.txt', package_dir='lib'):
        self.package_dir = package_dir
        self.packages = setuptools.find_packages(package_dir)

        self.all_authors = self._all_authors(authors_file)
        self.changes = open(os.path.join(self.here, changes_file)).read()
        self.readme = open(os.path.join(self.here, readme_file)).read()

    def _all_authors(self, authors_file):
        """Return the first author found."""
        st_author = self._text(os.path.join(self.here, authors_file))[0].strip()
        return [i.rstrip('>').strip() for i in st_author.split('<')]

    def _text(self, fname):
        """Return a list of lines non-empty neither that start with *#*."""
        STRIP_CHAR = '#'
        text = []

        with open(os.path.join(self.here, fname)) as fd:
            for ln in fd.readlines():
                if ln.startswith(STRIP_CHAR) or not ln.strip():
                    continue
                text.append(ln)
        return text

    def author(self):
        return self.all_authors[0]

    def author_email(self):
        return self.all_authors[1]

    def classifiers(self):
        return [c for c in classifiers.split('\n') if c]

    def description(self):
        """Return the docstring from a `package`."""
        package = self.packages[0]

        # Insert directory of the package in the path.
        if self.package_dir is not None and self.package_dir != '.':
            path = os.path.join(self.here, self.package_dir)
        else:
            path = self.here
        sys.path.insert(0, path)

        if '.' in package:
            pkg = __import__(package, level=1, fromlist=['*'])
        else:
            pkg = __import__(package, level=1)

        return pkg.__doc__.rstrip('.')

    def keywords(self):
        return [k for k in keywords.split('\n') if k]

    def long_description(self, header='Change history'):
        """Return the description from a text file."""
        if self.changes:
            header_ = '\n' + header + '\n' + ('=' * len(header)) + '\n\n'
            return self.readme + header_ + self.changes

        return self.readme

    def name(self):
        """Return the name of the project."""
        return os.path.basename(self.here)

    def url(self):
        return url

    def version(self):
        """Return the version found in the first line."""
        return self.changes.split('\n')[0].split(',')[0].lstrip('v')
# ===

get = Get()

setuptools.setup(
    install_requires=['Cython', 'Yamlog'],  # 'distribute'
    setup_requires=['Cython'],  #'distribute'
    tests_require=['nose', 'coverage'],

    package_dir={'': get.package_dir},
    packages=get.packages,
    ext_modules=[module],
    #cmdclass = dict(build_ext=Distutils.build_ext),

    include_package_data=True,
    test_suite='nose.collector',
    zip_safe=False,

    # Metadata
    # --------
    name=get.name(),
    version=get.version(),
    description=get.description(),
    long_description=get.long_description(),
    author=get.author(),
    author_email=get.author_email(),
    classifiers=get.classifiers(),
    keywords=get.keywords(),
    url=get.url(),
)
