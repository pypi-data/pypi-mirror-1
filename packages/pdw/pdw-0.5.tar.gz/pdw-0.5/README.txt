Public Domain Works Database and Web Application
************************************************

The PDW (Public Domain Works) package is the code which runs the Public Domain
Works DB, an open registry of artistic works that are in the public domain:

<http://www.publicdomainworks.net/> 

Though the project itself is focused on recording public domain works the code
and database schema provided by the PDW package is (intentionally) generic and
can be used to hold metadata on any kind of cultural material that fits into a
basic FRBR-like Work-Item-Person schema (see model/frbr.py for more details.)

The package also contains a variety of additional material such as:

  * Tools for cleaning up and normalized data
  * Scripts to import data from a wide variety of sources (MARC, Open Library
    JSON, NGCOBA)
  * Code for doing statistical analysis of the database

Install
=======

1. Install setuptools/easy_install

2. Install pdw.

EITHER direct from the Python package index:

  $ easy_install pdw

OR from a checkout of the mercurial repository:

    $ hg clone http://knowledgeforge.net/pdw/hg pdw
    $ cd pdw
    $ python setup.py develop

NB: we recommend installing into a python virtual environment using virtualenv.

3. Create a configuration File::

    $ paster make-config pdw <your-config.ini>

(Optional) Tweak the config file as needed.

4. Set up your DB, load some demo-data, and view it using the
web interface:

    $ paster --plugin=pdw db --config=<your-config.ini> create
    $ paster --plugin=pdw load --config=<your-config.ini> demo
    $ paster serve <your-config.ini>

You should now be able to see the web interface by visiting:

  <http://localhost:5000/>


Data Sources
************

data/composers.txt
==================

This data was kindly provided by Philip Harper:

  http://www.kingkong.demon.co.uk/
