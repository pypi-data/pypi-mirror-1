"""Setup the SMSShell application"""
import logging

import paste.deploy
from paste.deploy import appconfig
from pylons import config

from smsshell.config.environment import load_environment

log = logging.getLogger(__name__)

def setup_config(command, filename, section, vars):
    """Place any commands to setup smsshell here"""
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    paste.deploy.CONFIG.push_process_config({'app_conf':conf.local_conf,
                                             'global_conf':conf.global_conf})

    from smsshell import model
    engine = config['pylons.g'].sa_engine
    print "Creating tables"
    model.meta.create_all(bind=engine)

    print 'Adding default folders'
    for f in (u'Inbox', u'Archive', u'Outbox', u'Sent'):
        folder = model.Folder(
                name = f,
                commend = f,
            )
        model.Session.save(folder)
        model.Session.commit()

    print "Successfully setup."

