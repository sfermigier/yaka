About
=====

Yaka: when CRM meets enterprise social networking.


Install
=======

Prerequisites (native dependencies)
-----------------------------------

- Python 2.7
- A few image manipulation libraries (`libpng`, `libjpeg`...)
  [TODO: give the exact list.]
- `poppler-utils`
- `pip`

Python modules
--------------

Create a virtualenv (ex: `mkvirtualenv yaka`, assuming you have mkvirtualenv installed).

Then run `pip install -r deps.txt`.


Testing
=======

Short test
----------

Make sure all the dependencies are installed (cf. above), then
run `make test`.

With coverage
-------------

Run `make test-with-coverage`.

Full test suite
---------------

Install [tox](http://pypi.python.org/pypi/tox). Run `tox`.

On a VM
-------

1. Install [vagrant](http://vagrantup.com/) and Fabric (`pip install fabric`).

2. Download a box:

    vagrant box add precise64 http://files.vagrantup.com/precise64.box

3. Use `fabric` and `vagrant` to run tests:

    vagrant up
    fabric vagrant upgrade
    fabric vagrant setup
    fabric vagrant deploy


Deploy
======

(NOT WORKING YET).

1. Install `fabric` (`pip install fabric`).

2. Edit `fabfile.py` and change the configuration params.

3. Run `fab deploy`.


Build Status
============

The project is under continuous integration with Travis:

[![Build Status](https://secure.travis-ci.org/sfermigier/yaka-crm.png?branch=master)](https://secure.travis-ci.org/#!/sfermigier/yaka-crm)
