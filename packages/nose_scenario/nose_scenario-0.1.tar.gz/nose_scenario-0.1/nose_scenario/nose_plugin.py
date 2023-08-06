#! /usr/bin/python
# -*- coding: utf-8 -*-

# nose_scenario/nose_plugin.py
# Part of nose-scenario, a test scenario plug-in for nose
#
# Copyright © 2008 Ben Finney <ben+python@benfinney.id.au>
# Copyright © 2004, 2005, 2006, 2007, 2008 Canonical Ltd
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Implementation of nose plugin
"""

import os

import nose

from adapt import TestScenarioApplier


class ScenarioPlugin(nose.plugins.Plugin):
    """ Scenario application to loaded tests """

    name = "scenario"

    def make_test(self, obj, parent):
        """ Make test cases from the given object """
        print "Making test cases from %(obj)r, parent %(parent)r" % vars()
        scenarios = {}
        if hasattr(parent, 'scenarios'):
            scenarios.update(parent.scenarios)
        if hasattr(obj, 'scenarios'):
            scenarios.update(obj.scenarios)
        loader = nose.loader.TestLoader()
        suite = nose.suite.LazySuite()
        for testcase in loader.loadTestsFromTestClass(obj):
            applier = TestScenarioApplier(scenarios)
            map(suite.addTest, applier.adapt(testcase))
        for testcase in suite:
            yield testcase

    makeTest = make_test

    def test_name(self, test):
        """ Return a test name """
        testcase_str = str(test.test)
        scenario_id = getattr(test.test, 'scenario_id', None)
        if scenario_id is not None:
            testcase_str = "%(testcase_str)s [%(scenario_id)s]" % vars()
        return testcase_str

    testName = test_name

    def describe_test(self, test):
        """ Return a test description """
        testcase_desc = test.test.shortDescription()
        scenario_id = getattr(test.test, 'scenario_id', None)
        if testcase_desc is not None:
            if scenario_id is not None:
                testcase_desc = (
                    "%(testcase_desc)s"
                    " [Scenario: %(scenario_id)s]"
                    ) % vars()
        return testcase_desc

    describeTest = describe_test
