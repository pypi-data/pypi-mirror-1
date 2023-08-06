'''The PDW (Public Domain Works) package is the code which runs the Public Domain
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
'''
__version__ = '0.5'
def setup_config(config_file):
    import os
    config_path = os.path.abspath(config_file)
    if not os.path.exists(config_path):
        raise ValueError('No Configuration file exists at: %s' % config_path)
    import paste.deploy
    pasteconf = paste.deploy.appconfig('config:' + config_path)
    import pdw.config.environment
    pdw.config.environment.load_environment(pasteconf.global_conf,
        pasteconf.local_conf)

def conf():
    from pylons import config
    conf = config
    return conf

