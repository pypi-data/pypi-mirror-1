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

DEV_VERSION_STRING = "dev"

version = "0.1"
release = version

def version_string():
    if version is None:
        return DEV_VERSION_STRING
    return version

def release_string():
    if release is None:
        return DEV_VERSION_STRING
    return release

