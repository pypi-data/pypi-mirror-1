<%doc>
sender.mako - Template for monitoring the sender daemon

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

</%doc>

<%
import commands
%>

<%
output = commands.getoutput('ps ax | grep sms')
if output.find('smsbox') > -1:
    receiver_status = 'Running'
elsif output.find('start-stop') > -1:
    receiver_status = 'Starting'
else:
    receiver_status = 'Not Running %s' % h.link_to_remote('Start', dict(
            update='receiverStatus',
            url=h.url_for(controller='admin', action='restart_receiver')
        ))
%>
Receiver: 
${receiver_status}

