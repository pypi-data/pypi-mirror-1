"""base.py - base module for various utilities
"""

from sys import argv

import paste.deploy
from paste.deploy import appconfig
from pylons import config

from sqlchemistry import Config, Environment
from smsshell.config.environment import load_environment

(
        INBOX,
        ARCHIVE,
        OUTBOX,
    ) = range(1, 4)
NUMBER = '09283205839'
SERVER_CONF = '/etc/smsshell/server.ini'
CUSTOM_CONF = '/etc/smsshell/custom.ini'

custom_env = Environment(Config(CUSTOM_CONF))
space_sub = '_'

def setup(filename=SERVER_CONF):
    conf = appconfig('config:' + filename)
    load_environment(conf.global_conf, conf.local_conf)
    paste.deploy.CONFIG.push_process_config({'app_conf':conf.local_conf,
                                             'global_conf':conf.global_conf})
    from smsshell import model
    global model
    return model


