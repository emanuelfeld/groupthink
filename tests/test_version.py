#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of groupthink.
# https://github.com/dcgov/groupthink

# This project is in the public domain within the United States.
# Additionally, the Government of the District of Columbia waives
# copyright and related rights in the work worldwide through the CC0 1.0
# Universal public domain dedication.


from preggy import expect

from groupthink import __version__
from tests.base import TestCase


class VersionTestCase(TestCase):
    def test_has_proper_version(self):
        expect(__version__).to_equal('0.1.0')
