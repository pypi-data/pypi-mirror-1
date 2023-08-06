#! /usr/bin/python
# -*- coding: utf-8 -*-

# setup.py
# Part of nose-scenario, a test scenario plug-in for nose
#
# Copyright © 2008 Ben Finney <ben+python@benfinney.id.au>
# This is free software; you may copy, modify and/or distribute this work
# under the terms of the GNU General Public License, version 2 or later.
# No warranty expressed or implied. See the file LICENSE for details.

""" Package setup script
"""

import textwrap

from setuptools import setup, find_packages

main_package_name = 'nose_scenario'
main_package = __import__(main_package_name)

(short_description, long_description) = [
    textwrap.dedent(d).strip()
    for d in (main_package.__doc__.split('\n\n', 1))
    ]


setup(
    name = main_package_name,
    version = main_package._version,
    packages = find_packages(),

    # setuptools metadata
    zip_safe = False,

    # PyPI metadata
    entry_points = {
        'nose.plugins': [
            "scenario = nose_scenario.nose_plugin:ScenarioPlugin"],
        },
    author = main_package._author_name,
    author_email = main_package._author_email,
    description = short_description,
    license = main_package._license,
    keywords = "nose plugin test unittest scenario adapt",
    url = main_package._url,
    long_description = long_description,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        ],
    )
