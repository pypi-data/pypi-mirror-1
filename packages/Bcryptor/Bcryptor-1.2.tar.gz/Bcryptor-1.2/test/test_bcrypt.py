#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Bcryptor Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Test suite for the Bcrypt module."""

import bcryptor
from bcryptor import engine


class TestBcrypt():
    engine_ = engine.Engine(background=False)
    bcrypt = bcryptor.Bcrypt()

    COST = 6
    KEY = 'my pass'
    BAD_KEY = 'My pass'
    HASH = bcrypt.create(KEY)

    # Generating hashed passwords

    def test_create(self):
        """Should create a valid hash"""
        assert self.engine_._check_schema(self.HASH, len_hash=True)

    def test_compare_ok(self):
        """Should compare successfully to the original key"""
        assert self.bcrypt.valid(self.KEY, self.HASH)

    def test_compare_no(self):
        """Should compare unsuccessfully to the original key"""
        assert not self.bcrypt.valid(self.BAD_KEY, self.HASH)

    def test_cost_admin(self):
        """Should have default cost greater for superuser"""
        hash = self.bcrypt.create(self.KEY, admin=True)
        schema = self.bcrypt._split_schema(hash)
        assert int(schema[1]) == \
            self.bcrypt.default_cost + self.bcrypt.plus_admin_cost

    def test_cost_new_admin(self):
        """Should have cost greater for superuser"""
        hash = self.bcrypt.create(self.KEY, cost=self.COST, admin=True)
        schema = self.bcrypt._split_schema(hash)
        assert int(schema[1]) == self.COST + self.bcrypt.plus_admin_cost

    def test_length_salt_schema(self):
        salt = self.bcrypt._get_salt_schema(self.HASH)
        assert len(salt) == 29
