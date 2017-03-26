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

import xml.etree.ElementTree as ET
import sys, os
import sqlite3
from debparse import create_tables, BinaryPackage, SourcePackage

class RpmParser:
    def __init__(self, dbfile):
        # Default namespace in elementtree is so broken it is not even funny.
        self.ns = {'': 'http://linux.duke.edu/metadata/common',
                   'rpm': 'http://linux.duke.edu/metadata/rpm'}
        self.provides = {}
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
        create_tables(conn)

    def parse(self, bin_xml, src_xml):
        root = ET.parse(bin_xml).getroot()
#        packagetag = '{%s}%s' % (self.ns['default'], 'package')
        for package in root:
            if package.tag != '{%s}package' % self.ns['']:
                continue
            name = package.find('{%s}name' % self.ns['']).text
            deps = []
            description = package.find('{%s}description' % self.ns['']).text
            format = package.find('{%s}format' % self.ns[''])
            version = package.find('{%s}version' % self.ns['']).attrib['ver']
            provides = format.findall('rpm:provides', self.ns)
            requires = format.findall('rpm:requires', self.ns)
            for p in provides:
                for pp in p.findall('rpm:entry', self.ns):
                    provname = pp.attrib['name']
                    self.provides[provname] = name
            for r in requires:
                for rr in r.findall('rpm:entry', self.ns):
                    reqname = rr.attrib['name']
                    deps.append((reqname, None)) # FIXME add version requirement.
            self.bin_packages.append(BinaryPackage(name, version, description, deps))

    def to_db(self):
        self.bin_to_db()
#        self.src_to_db()

    def bin_to_db(self):
        c = self.conn.cursor()
        for p in self.bin_packages:
            try:
                c.execute('INSERT INTO bin_packages VALUES(?, ?, ?);', (p.name, p.version, p.description))
            except sqlite3.IntegrityError:
                print('Duplicate package name:', p.name)
                continue
        self.conn.commit()
        for package in self.bin_packages:
            for dep in package.depends:
                try:
                    required = self.provides[dep[0]]
                    version = dep[1]
                    if version is None:
                        version = ''
                    print(required)
                    c.execute('INSERT INTO depends VALUES(?, ?, ?);', (package.name, required, dep[1]))
                except sqlite3.Error as e:
                    print('Missing dep', required)
                    pass
                except KeyError as e:
                    print('Missing provides', dep[0])
        self.conn.commit()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('%s <db file> <binary package file> <source package file>' % sys.argv[0])
        sys.exit(0)
    debparser = RpmParser(sys.argv[1])
    debparser.parse(sys.argv[2], sys.argv[3])
    debparser.to_db()
    print('This script is unfinished. You probably want to use the sqlite file provided by Fedora instead.')
