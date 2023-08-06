import logging

from message import *

log = logging.getLogger(__name__)

class OutboxController(MessageController):
    entry_functions = (
            'edit',
            'details',
            'delete',
        )

    def _init_custom(self):
        c.columns_shown = [
                'recipient',
                'message',
                'created',
            ]
        c.column_descriptions['created'] = 'Schedule'

    def _list(self):
        c.entries = self.query.filter_by(folder=3)


