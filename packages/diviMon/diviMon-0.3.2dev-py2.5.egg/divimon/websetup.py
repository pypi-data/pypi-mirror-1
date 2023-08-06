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

    for t in ('Delivery Order', 'Delivery Receipt', 'Delivery Receipt Confirmed', ):
        entry = model.TransType(name=unicode(t))
        model.Session.save(entry)

    for p in ('Cash', 'Card', 'Cheque', ):
        entry = model.PayType(name=unicode(p))
        model.Session.save(entry)

    for ps in ('Paid', 'Unpaid', ):
        entry = model.PayStatus(name=unicode(ps))
        model.Session.save(entry)

    # Add non-existent areas, customers and agents
    for cnt in range(1, 4):
        entry = model.Area(name=u'Area %s' % cnt)
        model.Session.save(entry)
        agent = model.Agent(name=u'Agent %s' % cnt, area=cnt)
        model.Session.save(agent)
        customer = model.Customer(name=u'Customer %s' % cnt, area=cnt)
        model.Session.save(customer)

    for cheque_status in ('Unclaimed', 'Claimed', 'For Return', 'Returned'):
        entry = model.Cheque_status(name=unicode(cheque_status))
        model.Session.save(entry)

    model.Session.commit()

