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

import sys, os, sqlite3

def print_stats(dbfile):
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute('select dependency, count(name) from depends group by dependency order by count(name) desc limit 20;')
    print('Packages that are depended on the most\n')
    for l in c.fetchall():
        print(l[0], l[1])

    c.execute('select binary_package, count(source_package) from build_depends group by binary_package order by count(source_package) desc limit 20;')
    print('\n\nPackages that are build-depended on the most\n')
    for l in c.fetchall():
        print(l[0], l[1])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('%s <db file>' % sys.argv[0])
        sys.exit(0)
    print_stats(sys.argv[1])
