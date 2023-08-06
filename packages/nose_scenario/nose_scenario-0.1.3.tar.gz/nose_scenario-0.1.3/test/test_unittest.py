# -*- coding: utf-8 -*-

# test/test_unittest.py
# Part of nose-scenario, a test scenario plug-in for nose
#
# Copyright © 2008 Ben Finney <ben+python@benfinney.id.au>
# Copyright © 2004, 2005, 2006, 2007, 2008 Canonical Ltd
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Unit test for Python 'unittest' style tests
"""

import unittest

import sample_scenarios

class Test_Foo(unittest.TestCase):
    """ Test cases with docstrings """

    scenarios = sample_scenarios.scenarios

    def test_eggs_greater_than_spam(self):
        """ Foo eggs should be greater than spam """
        self.assertTrue(self.eggs > self.spam)

    def test_spam_is_not_negative(self):
        """ Foo spam should not be negative """
        self.assertTrue(self.spam >= 0)

class Test_Bar(unittest.TestCase):
    """ Test cases without docstrings """

    scenarios = sample_scenarios.scenarios

    def test_eggs_greater_than_spam(self):
        self.assertTrue(self.eggs > self.spam)

    def test_spam_is_not_negative(self):
        self.assertTrue(self.spam >= 0)
