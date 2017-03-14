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
import sqlite3

class DebParser:
    def __init__(self):
        self.packages = {}
        self.dbfile = 'debian.sqlite'
        if not os.path.exists(self.dbfile):
            self.create_db()
        self.conn = sqlite3.connect(self.dbfile)
        c = self.conn.cursor()
        c.execute('PRAGMA foreign_keys = ON;')
        self.conn.commit()

    def create_db(self):
        conn = sqlite3.connect(self.dbfile)
        c = conn.cursor()
        c.execute('''CREATE TABLE bin_packages(
        name TEXT NOT NULL PRIMARY KEY,
        version TEXT NOT NULL
        );''')
        c.execute('''CREATE TABLE depends(
        name TEXT NOT NULL,
        dependency TEXT NOT NULL,
        FOREIGN KEY(name) REFERENCES bin_packages(name),
        FOREIGN KEY(dependency) REFERENCES bin_packages(name)
        );''')
        conn.commit()
        conn.close()

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

    def to_db(self):
        c = self.conn.cursor()
        for name, p in self.packages.items():
            c.execute('INSERT INTO bin_packages VALUES(?, ?);', (name, p['Version']))
        self.conn.commit()
        for name, package in self.packages.items():
            if 'Depends' not in package:
                continue
            for depstr in package['Depends'].split(','):
                dep = depstr.split('(')[0].strip()
                c.execute('INSERT INTO depends VALUES(?, ?);', (name, dep))
        self.conn.commit()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('%d <package file>' % sys.argv[0])
        sys.exit(0)
    debparser = DebParser()
    debparser.parse(sys.argv[1])
    debparser.to_db()

