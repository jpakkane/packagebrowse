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

def split_depends(dep_entry):
    result = []
    for depstr in dep_entry.split(','):
        for alternates in depstr.split('|'):
            depsplit = alternates.split('(')
        if len(depsplit) == 1:
            version = None
        else:
            version = depsplit[1].split(''')''')[0]
        depname = depsplit[0].strip()
        if depname != '':
            result.append((depname, version))
        return result


class BinaryPackage:
    def __init__(self, name, version, description, depends):
        self.name = name
        self.version = version
        self.description = description
        self.depends = depends

    @classmethod
    def from_dict(cls, pdict):
        name = pdict['Package']
        version = pdict['Version']
        description = pdict['Description']
        depends = split_depends(pdict.get('Depends', ''))
        return BinaryPackage(name, version, description, depends)

class SourcePackage:
    def __init__(self, name, version, binaries, build_depends):
        self.name = name
        self.version = version
        self.binaries = binaries
        self.build_depends = build_depends

    @classmethod
    def from_dict(cls, pdict):
        name = pdict['Package']
        version = pdict['Version']
        binaries = [x.strip() for x in pdict['Binary'].split(',')]
        build_depends = split_depends(pdict.get('Build-Depends', ''))
        return SourcePackage(name, version, binaries, build_depends)

class DebParser:
    def __init__(self, dbfile):
        self.bin_packages = []
        self.src_packages = []
        self.dbfile = dbfile
        if not os.path.exists(self.dbfile):
            self.create_db()
        self.conn = sqlite3.connect(self.dbfile)
        c = self.conn.cursor()
        c.execute('PRAGMA foreign_keys = ON;')
        self.conn.commit()

    def create_db(self):
        conn = sqlite3.connect(self.dbfile)
        c = conn.cursor()
        
        # Tables for binary packages
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
        );''') # FIXME add uniquenes constraint to this and the one below.
        
        # Tables for source packages
        c.execute('''CREATE TABLE src_packages(
        name TEXT NOT NULL PRIMARY KEY,
        version TEXT NOT NULL
        );''')
        c.execute('''CREATE TABLE src_to_bin (
        source_package TEXT NOT NULL,
        binary_package TEXT NOT NULL,
        FOREIGN KEY(source_package) REFERENCES src_packages(name),
        FOREIGN KEY(binary_package) REFERENCES bin_packages(name)
        );''')
        c.execute('''CREATE TABLE build_depends(
        source_package TEXT NOT NULL,
        binary_package TEXT NOT NULL,
        version TEXT,
        FOREIGN KEY(source_package) REFERENCES src_packages(name),
        FOREIGN KEY(binary_package) REFERENCES bin_packages(name)
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

    def parse(self, bin_fname, src_fname):
        for packagedict in self.parse_debfile(bin_fname):
            bp = BinaryPackage.from_dict(packagedict)
            self.bin_packages.append(bp)
        for spkgdict in self.parse_debfile(src_fname):
            sp = SourcePackage.from_dict(spkgdict)
            self.src_packages.append(sp)

    def to_db(self):
        self.bin_to_db()
        self.src_to_db()

    def bin_to_db(self):
        c = self.conn.cursor()
        for p in self.bin_packages:
            try:
                c.execute('INSERT INTO bin_packages VALUES(?, ?, ?);', (p.name, p.version, p.description))
            except sqlite3.IntegrityError:
                # In ubuntu some bin_packages are in the file multiple times.
                continue
        self.conn.commit()
        for package in self.bin_packages:
            for dep in package.depends:
                try:
                    c.execute('INSERT INTO depends VALUES(?, ?, ?);', (package.name, dep[0], dep[1]))
                except sqlite3.Error as e:
                    print('Missing dep', dep[0])
                    pass
        self.conn.commit()

    def src_to_db(self):
        c = self.conn.cursor()
        for p in self.src_packages:
            try:
                c.execute('INSERT INTO src_packages VALUES(?, ?);', (p.name, p.version))
            except sqlite3.IntegrityError:
                print('Dupe src package', p.name)
                continue
        self.conn.commit()
        for p in self.src_packages:
            for d in p.binaries:
                try:
                    c.execute('INSERT INTO src_to_bin VALUES(?, ?);', (p.name, d))
                except sqlite3.IntegrityError:
                    print('Bad build-dep %s -> %s' % (p.name, d))
                    continue
        for package in self.src_packages:
            for dep in package.build_depends:
                try:
                    c.execute('INSERT INTO build_depends VALUES(?, ?, ?);', (package.name, dep[0], dep[1]))
                except sqlite3.Error as e:
                    print('Missing dep', dep[0])
                    pass
        self.conn.commit()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('%s <binary package file> <source package file>' % sys.argv[0])
        sys.exit(0)
    debparser = DebParser('debian.sqlite')
    debparser.parse(sys.argv[1], sys.argv[2])
    debparser.to_db()

