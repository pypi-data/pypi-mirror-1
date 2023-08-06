"""base.py - base module for various utilities
"""

from sys import argv

import paste.deploy
from paste.deploy import appconfig
from pylons import config

from smsshell.config.environment import load_environment

(
        INBOX,
        ARCHIVE,
        OUTBOX,
    ) = range(1, 4)
NUMBER = '09283205839'



def setup(filename='/opt/SMSShell/development.ini'):
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    paste.deploy.CONFIG.push_process_config({'app_conf':conf.local_conf,
                                             'global_conf':conf.global_conf})
    from smsshell import model
    global model
    return model

