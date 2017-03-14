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

import os, sys, sqlite3

class DbQuery:
    def __init__(self, dbfile):
        self.conn = sqlite3.connect(dbfile)

    def simple(self, packagename):
        c = self.conn.cursor()
        print('Dependencies of', packagename)
        c.execute('SELECT dependency FROM depends WHERE name = ?;', (packagename,))
        for d in c.fetchall():
            print(' ' + d[0])

        print('Reverse dependencies of', packagename)
        c.execute('SELECT DISTINCT name FROM depends WHERE dependency = ?;', (packagename, ))
        for d in c.fetchall():
            print(' ' + d[0])

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('%s dbfile packagename' % sys.argv[0])
        sys.exit(1)

    db = DbQuery(sys.argv[1])
    db.simple(sys.argv[2])

