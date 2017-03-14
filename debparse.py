#!/usr/bin/env python3

#  Copyright (C) 2017 Jussi Pakkanen.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of version 3, or (at your option) any later version,
# of the GNU General Public License as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os

class DebParser:
    def __init__(self):
        self.packages = {}

    def parse(self, fname):
        current = {}
        for line in open(fname):
            if line == '\n':
                self.packages[current['Package']] = current
                current = {}
                continue
            if line[0] == ' ':
                current['Description'] += line.rstrip()
            else:
                k, v = line.split(':', 1)
                current[k] = v.strip()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('%d <package file>' % sys.argv[0])
        sys.exit(0)
    debparser = DebParser()
    debparser.parse(sys.argv[1])
    print(debparser.packages['xwayland'])
