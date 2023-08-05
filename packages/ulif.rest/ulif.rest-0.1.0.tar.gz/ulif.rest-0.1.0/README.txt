
ulif.rest
*********

is a package that provides some ReStructuredText extensions. The
extensions collected in this package provide support for some of the
markup used in RestructuredText documents of the stock Python
documentation toolchain. Also a pygments directive (written by Georg
Brandl) is included, which enables syntax highlighting of code
fragments in reStructuredText docs with the ``pygments`` package.

See `README.txt` in the ``src/ulif/rest`` directory for API
documentation.

Note, that this is alphaware! Do not use it in productive
environments!

Prerequisites
=============

You need::

- Python 2.4. Rumors are, that also Python 2.5 will do.

- `setuptools`, available from 
  http://peak.telecommunity.com/DevCenter/setuptools

Other needed packages will be downloaded during
installation. Therefore you need an internet connection during
installation. 


Installation
============

Normally, this package should from other packages, that use it as a
helper lib. Thus, you do not have to care for installation. If you
want to integrate `ulif.rest` in your project, just declare
`ulif.rest` as a required package in your ``setup.py``.

with `buildout`
---------------

You can install this package with `buildout` as follows:


From the root of the package run::

     $ python2.4 bootstrap/bootstrap.py

This will download and install everything to run `buildout` in the
next step. Afterwards an executable script `buildout` should be
available in the freshly created `bin/` directory.

Next, fetch all needed packages, install them and create provided
scripts::

     $ bin/buildout

This should create a `test` script in `bin/`.

Running::

     $ bin/test

you can test the installed package.


with `easy_install`
-------------------

Run as a superuser::

     # easy_install ulif.rest

This should make the package available in your system Python.


Usage
=====

See `README.txt` and other .txt files in the ``src/ulif/rest/`` directory
for API documentation.

