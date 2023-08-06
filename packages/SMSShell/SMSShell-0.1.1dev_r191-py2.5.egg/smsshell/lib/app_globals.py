"""The application's Globals object"""
import re
from pylons import config

class Globals(object):
    """Globals acts as a container for objects available throughout the
    life of the application
    """

    def __init__(self):
        """One instance of Globals is created during application
        initialization and is available during requests via the 'g'
        variable
        """
        self.number = '09283205839'
        self.show_pages = 10
        self.function_delete = 'Delete'
        self.folder_inbox = 1
        self.folder_archive = 2
        self.folder_outbox = 3
        self.folder_sent = 4
        prefixes = ['^0', '^63', '^\+63', '^27763']
        self.prefixes = list(re.compile(pre) for pre in prefixes)

