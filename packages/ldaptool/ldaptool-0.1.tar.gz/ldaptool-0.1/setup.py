#!/usr/bin/env python
#
# ldaptool - LDAP manipulation tool
# Copyright (C) 2008  University of Bern
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import ldaptool.version


setup(
    name = "ldaptool",
    version = ldaptool.version.version_string(),
    description = "Tool for manipulating LDAP databases",
    author = "University of Bern",
    author_email = "grid-admin@id.unibe.ch",
    maintainer = "Philipp Bunge",
    maintainer_email = "buge@crimson.ch",
    license = "GNU General Public License (GPL)",
    url = "http://www.ox9.org/projects/ldaptool/",
    packages = find_packages(),
    scripts = ['bin/ldaptool'],
    platforms="any",
    test_suite = "tests",
    include_package_data = True,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
    ],
)

