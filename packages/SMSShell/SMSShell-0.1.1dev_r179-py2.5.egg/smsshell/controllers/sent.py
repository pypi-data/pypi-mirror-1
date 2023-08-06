import logging

from message import *

log = logging.getLogger(__name__)

class SentController(MessageController):

    def _init_custom(self):
        c.columns_shown = [
                'recipient',
                'message',
                'created',
            ]
        c.column_descriptions['created'] = 'Sent'

    def _list(self):
        c.entries = self.query.filter_by(folder=4)

