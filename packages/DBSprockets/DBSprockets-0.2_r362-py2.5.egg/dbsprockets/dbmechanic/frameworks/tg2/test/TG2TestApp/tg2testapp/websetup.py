"""Setup the TG2TestApp application"""
import logging

from paste.deploy import appconfig
from pylons import config

from tg2testapp.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup tg2testapp here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)

    # create model
    from tg2testapp import model
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.g'].sa_engine)
    model.DBSession.commit()

    print "Successfully setup"
