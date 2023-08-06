#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Bcryptor Authors
# Use of this source code is governed by the ISC License (LICENSE file).

"""Test suite for the wrapper engine."""

from nose import tools

from bcryptor import engine
import bcryptor


class TestEngine():
    engine_ = engine.Engine(background=False)
    bcrypt = bcryptor.Bcrypt()

    COST = 0
    BAD_COST = '7'
    KEY = 'wasup'
    SALT = engine_.generate_salt(COST)
    HASH = engine_.hash_key(KEY, SALT)

    # Generating BCrypt salts

    def test_salt_create(self):
        """Should return a string"""
        assert isinstance(self.SALT, str)

    def test_salt_random(self):
        """Should return random data"""
        assert self.SALT != self.engine_.generate_salt(self.COST)

    @tools.raises(TypeError)
    def test_salt_round(self):
        """Should raise TypeError"""
        self.engine_.generate_salt()

    @tools.raises(TypeError)
    def test_salt_round_numeric(self):
        """Should raise TypeError"""
        self.engine_.generate_salt(self.BAD_COST)

    def test_salt_round_min(self):
        """Should set the minimum round to 4"""
        for round in [-2, 0, 3]:
            h = self.engine_.generate_salt(round)
            info_hash = self.bcrypt._split_schema(h)  # Round is at position 1.
            assert int(info_hash[1]) == 4

    def test_salt_round_max(self):
        """Should set the maximum round to 31"""
        for round in [32, 256, 1023]:
            h = self.engine_.generate_salt(round)
            info_hash = self.bcrypt._split_schema(h)  # Round is at position 1.
            assert int(info_hash[1]) == 31

    # Generating BCrypt hashes

    def test_hash_create(self):
        """Should return a string"""
        assert isinstance(self.HASH, str)

    @tools.raises(TypeError)
    def test_hash_salt(self):
        """Should raise TypeError"""
        self.engine_.hash_key(self.KEY)

    @tools.raises(engine.SaltError)
    def test_hash_wrong_salt(self):
        """Should raise a SaltError"""
        self.engine_.hash_key(self.KEY, 'wrong_salt')

    @tools.raises(engine.HashError)
    def test_hash_wrong_hash(self):
        """Should raise a HashError"""
        self.engine_._check_schema(self.HASH[:-1], len_hash=True)

    @tools.raises(TypeError)
    def test_hash_key(self):
        """Should raise TypeError"""
        self.engine_.hash_key(None, self.SALT)

    @tools.raises(TypeError)
    def test_hash_key_numeric(self):
        """Should raise TypeError"""
        self.engine_.hash_key(5, self.SALT)
