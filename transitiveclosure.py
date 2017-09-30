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
from dbquery import DbQuery

def calculate_closure(dbfile, root_package):
    source_packages = set()
    binary_packages = set()
    src_to_process = set()
    bin_to_process = set()
    bin_to_process.add(root_package)
    dbq = DbQuery(dbfile)

    round = 0
    while len(src_to_process) > 0 or len(bin_to_process) > 0:
        print('Round', round)
        round += 1
        print('Source packages:', len(source_packages))
        print('Binary packages:', len(binary_packages))
        print('Source remaining:', len(src_to_process))
        print('Binary remaining:', len(bin_to_process))
        if len(src_to_process) > 1000000:
            s = src_to_process.pop()
            source_packages.add(s)
            trials = dbq.binary_packages_of(s)
            for tarr in trials:
                t = tarr[0]
                if t not in binary_packages:
                    bin_to_process.add(t)
        if len(bin_to_process) > 0:
            p = bin_to_process.pop()
            #binary_packages.add(p)
            trials = dbq.reverse_build_deps_of(p)
            for t in trials:
                if t not in binary_packages:
                    binary_packages.add(t)
                    bin_to_process.add(t)
    sf = open('sources.txt', 'w')
    for s in sorted(source_packages):
        sf.write(s + '\n')
    sf.close()
    pf = open('binaries.txt', 'w')
    print('Evaluating binary packages')
    for p in binary_packages:
        source_packages.add(dbq.source_package_of(p))
    sf = open('sources.txt', 'w')
    for s in sorted(source_packages):
        sf.write(s + '\n')
    sf.close()
    for p in sorted(binary_packages):
        pf.write(p + '\n')
    pf.close()
    print(len(source_packages))
    print(len(binary_packages))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('%s <db file>' % sys.argv[0])
        sys.exit(0)
    calculate_closure(sys.argv[1], 'qtdeclarative5-dev')
