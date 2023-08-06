import logging

from message import *

log = logging.getLogger(__name__)

class ArchiveController(MessageController):

    def _init_custom(self):
        c.columns_shown = [
                'sender',
                'recipient',
                'message',
                'created',
            ]
        c.column_descriptions['created'] = 'Received'

    def _list(self):
        c.entries = self.query.filter_by(folder=2)

