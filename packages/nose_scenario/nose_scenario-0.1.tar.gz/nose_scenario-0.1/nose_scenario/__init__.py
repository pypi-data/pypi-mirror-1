#! /usr/bin/python
# -*- coding: utf-8 -*-

# nose_scenario/__init__.py
# Part of nose-scenario, a test scenario plug-in for nose
#
# Copyright © 2008 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Scenario adaptor for nose tests

    Adapt parameterised test cases with scenario data, generating
    unique test cases for each scenario.

    """

_version = "0.1"
_date = "2008-07-17"
_author_name = "Ben Finney"
_author_email = "ben+python@benfinney.id.au"
_author = "%(_author_name)s <%(_author_email)s>" % vars()
_copyright = "Copyright © %s %s" % (
    _date.split('-')[0], _author_name
)
_license = "GPL"
_url = "http://cheeseshop.python.org/pypi/nose-scenario/"
