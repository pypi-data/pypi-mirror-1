"""Setup the pdw application"""
import logging

from paste.deploy import appconfig
from pylons import config

from pdw.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup pdw here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)

    from pdw import model
    log.info('Creating tables')
    model.binddb()
    model.repo.create_db()
    log.info('Creating tables: SUCCESS')
