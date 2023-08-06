"""Folder Controller

AUTHOR: Emanuel Gardaya Calso

Last Modified:
    2008-03-17
    2008-03-18

"""

import logging

from smsshell.lib.base import *

log = logging.getLogger(__name__)


class LabelController(ListController):
    table = model.Label
    children = dict(
            message = dict(
                    table=model.Message,
                    columns=('sender', 'recipient', 'message'),
                )
        )


