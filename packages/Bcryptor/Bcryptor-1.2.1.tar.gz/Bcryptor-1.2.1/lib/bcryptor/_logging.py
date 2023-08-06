#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009-2010, the Bcryptor Authors
# Use of this source code is governed by the ISC License (LICENSE file).

import logging


class NullHandler(logging.Handler):
    """A handler which does nothing."""
    def emit(self, record):
        pass


# Do-nothing handler
null_handler = NullHandler()
logging.getLogger('').addHandler(null_handler)
