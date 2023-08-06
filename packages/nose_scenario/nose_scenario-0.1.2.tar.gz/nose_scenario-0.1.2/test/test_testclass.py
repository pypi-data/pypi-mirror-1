# -*- coding: utf-8 -*-

# test/test_testclass.py
# Part of nose-scenario, a test scenario plug-in for nose
#
# Copyright © 2008 Ben Finney <ben+python@benfinney.id.au>
# Copyright © 2004, 2005, 2006, 2007, 2008 Canonical Ltd
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Unit test for nose-style test class
"""

import nose

import sample_scenarios

class Test_Foo(object):
    """ Test cases with docstrings """

    scenarios = sample_scenarios.scenarios

    def test_eggs_greater_than_spam(self):
        """ Foo eggs should be greater than spam """
        nose.tools.assert_true(self.eggs > self.spam)

    def test_spam_is_not_negative(self):
        """ Foo spam should not be negative """
        nose.tools.assert_true(self.spam >= 0)

class Test_Bar(object):
    """ Test cases without docstrings """

    scenarios = sample_scenarios.scenarios

    def test_eggs_greater_than_spam(self):
        nose.tools.assert_true(self.eggs > self.spam)

    def test_spam_is_not_negative(self):
        nose.tools.assert_true(self.spam >= 0)
