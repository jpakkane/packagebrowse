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

class BinaryPackage:
    def __init__(self, pdict):
        self.name = pdict['Package']
        self.version = pdict['Version']
        self.description = pdict['Description']
        self.depends = []
        for depstr in pdict.get('Depends', '').split(','):
            for alternates in depstr.split('|'):
                depsplit = alternates.split('(')
                if len(depsplit) == 1:
                    version = None
                else:
                    version = depsplit[1].split(''')''')[0]
                depname = depsplit[0].strip()
                if depname != '':
                    self.depends.append((depname, version))

class DebParser:
    def __init__(self):
        self.packages = []
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
        version TEXT NOT NULL,
        description TEXT NOT NULL
        );''')
        c.execute('''CREATE TABLE depends(
        name TEXT NOT NULL,
        dependency TEXT NOT NULL,
        version TEXT,
        FOREIGN KEY(name) REFERENCES bin_packages(name),
        FOREIGN KEY(dependency) REFERENCES bin_packages(name)
        );''')
        conn.commit()
        conn.close()

    def parse_debfile(self, fname):
        packages = []
        current = {}
        last_key = None
        for line in open(fname):
            if line == '\n':
                packages.append(current)
                current = {}
                continue
            if line[0] == ' ':
                current[last_key] += '\n' + line.strip()
            else:
                k, v = line.split(':', 1)
                current[k] = v.strip()
                last_key = k
        return packages

    def parse(self, fname):
        for packagedict in self.parse_debfile(fname):
            bp = BinaryPackage(packagedict)
            self.packages.append(bp)

    def to_db(self):
        c = self.conn.cursor()
        for p in self.packages:
            try:
                c.execute('INSERT INTO bin_packages VALUES(?, ?, ?);', (p.name, p.version, p.description))
            except sqlite3.IntegrityError:
                # In ubuntu some packages are in the file multiple times.
                continue
        self.conn.commit()
        for package in self.packages:
            for dep in package.depends:
                try:
                    c.execute('INSERT INTO depends VALUES(?, ?, ?);', (package.name, dep[0], dep[1]))
                except sqlite3.Error as e:
                    print('Missing dep', dep[0])
                    pass
        self.conn.commit()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('%d <package file>' % sys.argv[0])
        sys.exit(0)
    debparser = DebParser()
    debparser.parse(sys.argv[1])
    debparser.to_db()

