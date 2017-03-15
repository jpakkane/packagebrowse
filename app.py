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

from flask import Flask
from flask import request
import dbquery

app = Flask(__name__)

db = dbquery.DbQuery('debian.sqlite')

frontpage = '''<html>
<head></head>
<body>
<h1>Distro package database</h1>
<p>Search for packages.</p>

<p>
<form action="search" method="post">
Package name: <input type="text" name="name"><br>
<input type="submit" value="submit">
</form>
</p>
</body></html>'''

@app.route("/")
def hello():
    return frontpage

@app.route('/search', methods=['POST'])
def search():
    templ = '''<html><head></head><body><h1>Source packages</h1>
<p>
<ul>
%s
</ul>
</p>
<h1>Binary packages</h1>
<p>
<ul>
%s
</ul>
</p>
<p><hr><a href="/">Back to front page</a></p>
</body></html>'''
    res_templ = '''<li><a href="/%s/%s">%s</a></li>'''
    src_packages = db.search_source_packages(request.form['name'])
    src_lines = [res_templ % ('show_src', x[0], x[0]) for x in src_packages]
    bin_packages = db.search_binary_packages(request.form['name'])
    bin_lines = [res_templ % ('show_bin', x[0], x[0]) for x in bin_packages]
    return templ % (' '.join(src_lines), ' '.join(bin_lines))

@app.route('/show_src/<package_name>')
def show_src(package_name):
    pkg = db.source_package_info(package_name)
    templ = '''<html><head></head><body><h1>Source package %s</h1>
    <p>Version: %s</p>
    <h2>Binary packages generated from this package</h2>
    <p><ul>%s</ul></p>
    <h2>Build dependencies</h2>
    <p><ul>%s</ul></p>
<hr><a href="/">Back to front page</a></p>
</body></html>'''
    line_templ = '<li><a href="/show_bin/%s">%s</a></li>\n'
    bins = [line_templ % (p, p) for p in pkg.binaries]
    builddeps = [line_templ % (p[0], p[0]) for p in pkg.build_depends]
    return templ % (pkg.name, pkg.version, ' '.join(bins), ' '.join(builddeps))

@app.route('/show_bin/<package_name>')
def show_bin(package_name):
    pkg = db.binary_package_info(package_name)
    templ = '''<html><head></head><body><h1>Binary package %s</h1>
    <p>Version: %s</p>
    <p>Source package: <a href="/show_src/%s">%s</a></p>
    <h2>Dependencies</h2>
    <p><ul>%s</ul></p>
    <h2>Reverse dependencies</h2>
    <p><ul>%s</ul></p>
    <h2>Build dependencies</h2>
    <p><ul>%s</ul></p>
    <h2>Reverse build dependencies</h2>
    <p><ul>%s</ul></p>
<hr><a href="/">Back to front page</a></p>
</body></html>'''
    dep_templ = '<li><a href="/show_bin/%s">%s</a></li>\n'
    rdep_templ = '<li><a href="/show_bin/%s">%s</a></li>\n'
    bdep_templ = '<li><a href="/show_bin/%s">%s</a></li>\n'
    rbdep_templ = '<li><a href="/show_bin/%s">%s</a></li>\n'
    src_pkg = db.source_package_of(package_name)
    rdep_pkgs = db.reverse_deps_of(package_name)
    bdep_pkgs = db.build_deps_for_src(src_pkg)
    rbdep_pkgs = db.reverse_build_deps_of(package_name)
    deps = [dep_templ % (p[0], p[0]) for p in pkg.depends]
    rdeps = [rdep_templ % (p[0], p[0]) for p in rdep_pkgs]
    bdeps = [bdep_templ % (p[0], p[0]) for p in bdep_pkgs]
    rbdeps = [bdep_templ % (p, p) for p in rbdep_pkgs]
    return templ % (pkg.name, pkg.version, src_pkg, src_pkg, ' '.join(deps),
                    ' '.join(rdeps), ' '.join(bdeps), ' '.join(rbdeps))

if __name__ == '__main__':
    app.run()
