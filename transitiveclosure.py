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
    bin_to_process = set()
    bin_to_process.add(root_package)
    processed_bins = set()
    dbq = DbQuery(dbfile)

    round = 0
    while len(bin_to_process) > 0:
        round += 1
        if round % 100 == 0:
            print('Round', round)
            print('Binary packages:', len(binary_packages))
            print('Binary remaining:', len(bin_to_process))
        if len(bin_to_process) > 0:
            p = bin_to_process.pop()
            processed_bins.add(p)
            trials = dbq.reverse_build_deps_of(p)
            for t in trials:
                if t not in binary_packages and t not in processed_bins:
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
    if len(sys.argv) != 3:
        print('%s <db file> <package>' % sys.argv[0])
        sys.exit(0)
    calculate_closure(sys.argv[1], sys.argv[2])
