"""Setup the diviMon application"""
import logging

import paste.deploy
from paste.deploy import appconfig
from pylons import config

from divimon.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup divimon here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    paste.deploy.CONFIG.push_process_config({'app_conf':conf.local_conf,
                                             'global_conf':conf.global_conf})

    from divimon import model
    engine = config['pylons.g'].sa_engine
    print 'Creating database tables'
    model.meta.create_all(bind=engine)
    print 'Creating default entries'
    for t in ('Sales Order', 'Delivery Receipt', 'Purchase Order', 'Purchase Receipt', 'Purchase Return', ):
        entry = model.TransType(name=unicode(t))
        model.Session.save(entry)
    #for c in ('Fuel', 'Service', 'Treats', ):
        #entry = model.Classification(name=unicode(c))
        #model.Session.save(entry)
    for p in ('Cash', 'Card', 'Cheque', ):
        entry = model.PayType(name=unicode(p))
        model.Session.save(entry)

    # Add non-existent area
    for area in ('Area 3', 'Area 2', 'Area 1', ):
        entry = model.Area(name=unicode(area))
        model.Session.save(entry)
    model.Session.commit()

