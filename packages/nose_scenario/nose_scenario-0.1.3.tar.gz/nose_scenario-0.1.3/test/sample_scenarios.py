# -*- coding: utf-8 -*-

# test/sample_scenarios.py
# Part of nose-scenario, a test scenario plug-in for nose
#
# Copyright © 2008 Ben Finney <ben+python@benfinney.id.au>
# Copyright © 2004, 2005, 2006, 2007, 2008 Canonical Ltd
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Sample scenarios for test cases
"""

scenarios = {
    'wibble': dict(
        spam=23,
        eggs=12,
        ),
    'wobble': dict(
        spam=0,
        eggs=74,
        ),
    'warble': dict(
        spam=-2,
        eggs=1,
        ),
    }
