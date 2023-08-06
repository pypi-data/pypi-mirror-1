# Copyright 2009 Neil Martinsen-Burrell

# This file is part of mcrepogen
#
# mcrepogen is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# 5-tuple representing the current version
version_info = (0,3,0,'final',0)

def format_version_info(version_info):

    if version_info[2] == 0:
        formatted = '%d.%d' % version_info[:2]
    else:
        formatted = '%d.%d.%d' % version_info[:3]
    if version_info[3] != 'final':
        formatted += version_info[3]
        if version_info[4] != 0:
            formatted += '%s' % version_info[4]
    return formatted

version_str = format_version_info(version_info)
