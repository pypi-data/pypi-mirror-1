import time
import commands
import logging

from smsshell.lib.base import *

log = logging.getLogger(__name__)
script = {}
script['sender'] = 'sender.py restart'
script['receiver'] = 'start-stop-sms.sh start'


class AdminController(BaseController):

    def index(self):
        # Return a rendered template
        #   return render('/some/template.mako')
        # or, Return a response
        return 'Hello World'

    def show_restart(self):
        return 'Restarting <a href="#" onclick="showStatus()">Refresh Page</a>'

    def restart_sender(self):
        output = commands.getstatusoutput(script['sender'])
        return render('/admin/sender.mako')

    def restart_receiver(self):
        output = commands.getstatusoutput(script['receiver'])
        return render('/admin/receiver.mako')

    def start_sender(self):
        output = commands.getstatusoutput(script['sender'])
        return render('/admin/sender.mako')

    def start_receiver(self):
        output = commands.getstatusoutput(script['receiver'])
        return render('/admin/receiver.mako')

    def show_status_sender(self):
        return render('/admin/sender.mako')

    def show_status_receiver(self):
        return render('/admin/receiver.mako')

