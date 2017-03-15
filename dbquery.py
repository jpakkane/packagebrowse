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
        c.execute('''SELECT source_package FROM src_to_bin WHERE binary_package = ?''', (packagename,))
        src_name = c.fetchone()[0]
        print('Dependencies of', packagename)
        c.execute('SELECT dependency FROM depends WHERE name = ? ORDER BY dependency;', (packagename,))
        for d in c.fetchall():
            print(' ' + d[0])

        print('Reverse dependencies of', packagename)
        c.execute('SELECT DISTINCT name FROM depends WHERE dependency = ? ORDER BY name;', (packagename, ))
        for d in c.fetchall():
            print(' ' + d[0])

        print('Build-dependencies of', packagename)
        c.execute('SELECT binary_package FROM build_depends WHERE source_package = ?', (src_name,))
        for d in c.fetchall():
            print(' ' + d[0])
        print('Reverse build-dependencies of', packagename)
        c.execute('''SELECT binary_package FROM src_to_bin WHERE source_package IN
        (SELECT DISTINCT source_package FROM build_depends WHERE binary_package = ?);''', (packagename,))
        for d in c.fetchall():
            print(' ' + d[0])

    def stats(self):
        c = self.conn.cursor()
        c.execute('SELECT COUNT(*) FROM bin_packages;')
        print('%s packages' % c.fetchone()[0])
        c.execute('SELECT COUNT(*) FROM depends;')
        print('%s dependencies' % c.fetchone()[0])
        c.execute('SELECT COUNT(*) FROM src_packages;')
        print('%s source packages' % c.fetchone()[0])
        c.execute('SELECT COUNT(*) FROM build_depends;')
        print('%s build dependencies' % c.fetchone()[0])

    def search_source_packages(self, term):
        c = self.conn.cursor()
        c.execute('SELECT name from src_packages WHERE name LIKE ?;', (term + '%',))
        return c.fetchall()

    def search_binary_packages(self, term):
        c = self.conn.cursor()
        c.execute('SELECT name from bin_packages WHERE name LIKE ?;', (term + '%',))
        return c.fetchall()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('%s dbfile packagename' % sys.argv[0])
        sys.exit(1)

    db = DbQuery(sys.argv[1])
    db.stats()
    db.simple(sys.argv[2])
    
