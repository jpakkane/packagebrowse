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

import urllib.request
import gzip

fedora_packages = 'http://www.nic.funet.fi/pub/Linux/INSTALL/fedora/linux/releases/25/Workstation/x86_64/os/repodata/f5cccd21680ca57b140e5d891ca9fedf5dafde16701f78aaf4cae83fc8eddbde-primary.xml.gz'
fedora_sources = 'http://www.nic.funet.fi/pub/Linux/INSTALL/fedora/linux/releases/25/Workstation/source/tree/repodata/f0ecf609b4e5c511b8241c1d8c56186b21b514ce77795718916f668b4ae764f3-primary.xml.gz'

debian_packages = 'http://ftp.fi.debian.org/debian/dists/unstable/main/binary-amd64/Packages.gz'
debian_sources = 'http://ftp.fi.debian.org/debian/dists/unstable/main/source/Sources.gz'

def dl():
    open('fedora.xml', 'wb').write(gzip.open(urllib.request.urlopen(fedora_packages)).read())
    open('fedora-src.xml', 'wb').write(gzip.open(urllib.request.urlopen(fedora_sources)).read())
    open('debian.packages', 'wb').write(gzip.open(urllib.request.urlopen(debian_packages)).read())
    open('debian-src.packages', 'wb').write(gzip.open(urllib.request.urlopen(debian_sources)).read())

if __name__ == '__main__':
    dl()
