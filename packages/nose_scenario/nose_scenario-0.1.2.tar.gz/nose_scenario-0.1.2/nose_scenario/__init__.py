#! /usr/bin/python
# -*- coding: utf-8 -*-

# nose_scenario/__init__.py
# Part of nose-scenario, a test scenario plug-in for nose
#
# Copyright © 2008 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" test scenario adaptation plugin for nose

    The 'scenario' plugin for 'nose' enables any test case to be
    transformed into multiple copies of that test, each adapted for a
    specific test scenario.

    The plugin will detect scenarios associated with one or more test
    cases. It then generates a number of adapted copies of each test
    case, one for each scenario, with the scenario data exposed to the
    test case via attributes. Each adapted test case will then be run
    separately by 'nose', and will be identified distinctly by the
    scenario used.

    'nose' is a testing framework for Python code.

    """

_version = "0.1.2"
_date = "2008-07-19"
_author_name = "Ben Finney"
_author_email = "ben+python@benfinney.id.au"
_author = "%(_author_name)s <%(_author_email)s>" % vars()
_copyright = "Copyright © %s %s" % (
    _date.split('-')[0], _author_name
)
_license = "GPL"
_url = "http://cheeseshop.python.org/pypi/nose_scenario/"
