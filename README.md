# Debian package database browser

This is a simple app that downloads the Debian package list and makes it browsable.

For each package it shows both direct and reverse dependencies and build-dependencies.

Preparation steps:

    ./downloadfiles
    ./debparse.py debian.sqlite debian.packages debian-src.packages

After this you can run the `stats.py` script that counts some stats or `app.py` which is a simple Flask application that provides a web interface for the package list.
