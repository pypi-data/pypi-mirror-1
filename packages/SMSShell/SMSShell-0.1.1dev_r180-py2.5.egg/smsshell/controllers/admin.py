import time
import commands
import logging

from smsshell.lib.base import *

log = logging.getLogger(__name__)
script = {}
script['sender'] = 'sender.py restart'
script['reciever'] = 'start-stop-sms.sh start'


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

    def restart_reciever(self):
        output = commands.getstatusoutput(script['reciever'])
        return render('/admin/reciever.mako')

    def start_sender(self):
        output = commands.getstatusoutput(script['sender'])
        return render('/admin/sender.mako')

    def start_reciever(self):
        output = commands.getstatusoutput(script['reciever'])
        return render('/admin/reciever.mako')

    def show_status_sender(self):
        return render('/admin/sender.mako')

    def show_status_reciever(self):
        return render('/admin/reciever.mako')

