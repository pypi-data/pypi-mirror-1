"""Estate Controller

AUTHOR Emanuel Gardaya Calso

"""

import logging

from smsshell.lib.base import *

log = logging.getLogger(__name__)

class EstateController(ListController):
    table = model.Estate

