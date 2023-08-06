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

from adapt import AdaptedTestLoader


class ScenarioPlugin(nose.plugins.Plugin):
    """ Scenario application to loaded tests """

    name = "scenario"

    def prepare_test_loader(self, loader):
        return AdaptedTestLoader()

    prepareTestLoader = prepare_test_loader

    def make_test(self, obj, parent):
        """ Make test cases from the given object """
        print "Making test cases from %(obj)r, parent %(parent)r" % vars()
        scenarios = {}
        if hasattr(parent, 'scenarios'):
            scenarios.update(parent.scenarios)
        if hasattr(obj, 'scenarios'):
            scenarios.update(obj.scenarios)

        suite = AdaptedTestSuite(scenarios)
        suite.add_test(obj)
        return suite

    makeTest = make_test
