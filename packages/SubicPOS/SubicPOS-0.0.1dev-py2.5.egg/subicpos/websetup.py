"""Setup the SubicPOS application"""
import logging

import paste.deploy
from paste.deploy import appconfig
from pylons import config

from subicpos.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup subicpos here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    paste.deploy.CONFIG.push_process_config({'app_conf':conf.local_conf,
                                             'global_conf':conf.global_conf})

    from subicpos import model
    engine = config['pylons.g'].sa_engine
    print 'Creating database tables'
    model.meta.create_all(bind=engine)
    print 'Creating default entries'
    for t in ('Fuel', 'Service', 'Treats', 'Delivered', 'Returns', 'Waste', 'Consumed', ):
        entry = model.TransType(name=unicode(t))
        model.Session.save(entry)
    for c in ('Fuel', 'Service', 'Treats', ):
        entry = model.Classification(name=unicode(c))
        model.Session.save(entry)
    for p in ('Cash', 'Card', 'Cheque', 'Fleet', ):
        entry = model.PayType(name=unicode(p))
        model.Session.save(entry)

    # Add non-existent branches
    entry = model.Branch(name=u'Branch 1')
    model.Session.save(entry)
    model.Session.commit()

