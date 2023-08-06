#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Bcryptor Authors
# Use of this source code is governed by the ISC License (LICENSE file).

import yamlog


def setup_package():
    """Will be executed before tests are run."""
    yamlog.setup()


def teardown_package():
    """Will be executed after all tests have run."""
    yamlog.teardown()
