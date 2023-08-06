#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Bcryptor Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Cython declarations."""

cdef extern from "src/bcrypt.c":
    char* bcrypt(char* key, char* salt)
    char* bcrypt_gensalt_linux(unsigned char log_rounds, unsigned char* salt)
