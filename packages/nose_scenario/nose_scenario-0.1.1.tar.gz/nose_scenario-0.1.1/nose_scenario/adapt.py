# -*- coding: utf-8 -*-

# nose_scenario/adapt.py
# Part of nose-scenario, a test scenario plug-in for nose
#
# Copyright © 2008 Ben Finney <ben+python@benfinney.id.au>
# Copyright © 2004, 2005, 2006, 2007, 2008 Canonical Ltd
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Adaptation of test cases to scenarios
"""

# Based on Canonical's bzrlib.tests.TestScenarioApplier

import unittest
import copy

import nose


class TestScenarioApplier(object):
    """ A tool to apply scenarios to tests. """

    def __init__(self, scenarios=None):
        """ Initialise the applier with scenarios

            :param scenarios:
                A mapping from scenario ID to scenario attributes,
                where each item is as defined for ``AdaptedTest``.
            :return: None

            """
        self.scenarios = scenarios

    def adapt(self, testcase):
        """ Generate a copy of `testcase` for each scenario. """
        if self.scenarios is not None:
            for scenario in self.scenarios.items():
                adapted_testcase = AdaptedTest(testcase, scenario)
                yield adapted_testcase
        else:
            yield testcase


class AdaptedTest(nose.case.Test):
    """ A test case adapted for a specific scenario """

    def __init__(self, testcase, scenario, *args, **kwargs):
        """ Set up a copy of `testcase` with `scenario` applied to it.

            :param testcase: A `nose.case.Test` instance to adapt.
            :param scenario: A tuple describing the scenario.
                First element: The scenario id.
                Second element: Dict containing attributes to set on
                the test.
            :return: None

            """
        super(AdaptedTest, self).__init__(
            copy.copy(testcase.test), *args, **kwargs)

        (scenario_id, scenario_attributes) = scenario
        self.test.scenario_id = scenario_id
        for name, value in scenario_attributes.items():
            setattr(self.test, name, value)

        self.test.id = self._make_testcase_id_func()
        self.test.__str__ = self._make_testcase_str_func()
        self.test.__repr__ = self._make_testcase_repr_func()
        self.test.shortDescription = self._make_testcase_short_desc_func()

    def _make_testcase_id_func(self):
        orig_testcase_id = self.test.id()
        scenario_id = self.test.scenario_id
        testcase_id = "%(orig_testcase_id)s[%(scenario_id)s]" % vars()
        def get_testcase_id():
            return testcase_id
        return get_testcase_id

    def _make_testcase_str_func(self):
        orig_testcase_str = str(self.test)
        scenario_id = self.test.scenario_id
        testcase_str = "%(orig_testcase_str)s [%(scenario_id)s]" % vars()
        def get_testcase_str():
            return testcase_str
        return get_testcase_str

    def _make_testcase_repr_func(self):
        return self._make_testcase_str_func()

    def _make_testcase_short_desc_func(self):
        orig_testcase_desc_func = getattr(
            self.test, 'shortDescription',
            self._make_testcase_str_func())
        orig_testcase_desc = orig_testcase_desc_func()
        scenario_id = self.test.scenario_id
        if orig_testcase_desc is not None:
            testcase_desc = (
                "%(orig_testcase_desc)s"
                " [Scenario: %(scenario_id)s]"
                ) % vars()
        else:
            testcase_desc = None
        def get_testcase_desc():
            return testcase_desc
        return get_testcase_desc


base_suite_class = nose.suite.ContextSuite

class AdaptedTestSuite(base_suite_class):
    """ Test suite that adapts test cases when added """

    def __init__(self, tests=(), scenarios=None, *args, **kwargs):
        """ Initialise the test suite with scenarios for test cases

            :param tests:
                An iterable of test cases to be adapted and added.
            :param scenarios:
                A mapping of test scenarios to be applied to each test
                case, as defined for ``AdaptedTest``.

            """
        self.scenarios = scenarios
        super(AdaptedTestSuite, self).__init__(tests, *args, **kwargs)

    def add_tests(self, collection):
        """ Add and adapt one or more tests to the suite

            :param collection:
                An iterable of test cases to be adapted and added.
            :return: None

            Each specified test case will be adapted by a
            ``TestScenarioApplier`` using the ``scenarios`` used to
            create this suite. The result will be that each test case
            is adapted and added multiple times, once for each
            scenario.

            """
        applier = TestScenarioApplier(self.scenarios)
        for testcase in collection:
            for adapted_testcase in applier.adapt(testcase):
                super(AdaptedTestSuite, self).addTest(adapted_testcase)

    addTests = add_tests


base_loader_class = nose.loader.defaultTestLoader

class AdaptedTestLoader(base_loader_class):
    """ Test loader that adapts test cases when loaded """

    suite_class = suiteClass = AdaptedTestSuite

    def load_tests_from_test_case(self, testCaseClass):
        super_instance = super(AdaptedTestLoader, self)
        base_suite = super_instance.loadTestsFromTestCase(testCaseClass)
        scenarios = getattr(testCaseClass, 'scenarios', None)
        suite = self.suite_class(iter(base_suite), scenarios)
        return suite

    loadTestsFromTestCase = load_tests_from_test_case

    def load_tests_from_test_class(self, cls):
        super_instance = super(AdaptedTestLoader, self)
        base_suite = super_instance.loadTestsFromTestClass(cls)
        scenarios = getattr(cls, 'scenarios', None)
        suite = self.suite_class(iter(base_suite), scenarios)
        return suite

    loadTestsFromTestClass = load_tests_from_test_class
