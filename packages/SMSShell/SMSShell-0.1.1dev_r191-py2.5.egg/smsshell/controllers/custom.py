import logging

from smsshell.lib.base import *
from sqlchemistry import Config, Environment

log = logging.getLogger(__name__)


class CustomController(BaseController):

    def index(self):
        self.conf = Config('/etc/smsshell/custom.ini')
        self.env = Environment(self.conf)
        tbl_names = self.env.tables.keys()
        # Return a rendered template
        #   return render('/some/template.mako')
        # or, Return a response
        return tbl_names

    def show_columns(self):
        table = request.params['table']
        self.conf = Config('/etc/smsshell/custom.ini')
        self.env = Environment(self.conf)
        c.columns = self.env.tables[table].c.keys()
        return c.columns

