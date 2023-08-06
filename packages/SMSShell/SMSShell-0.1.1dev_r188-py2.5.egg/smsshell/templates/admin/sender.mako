<%doc>
sender.mako - Template for monitoring the sender daemon

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

</%doc>

<%
import commands
%>

<%
output = commands.getoutput('ps ax | grep sender')
if output.find('sender.py') > -1 and output.find('python') > -1:
    sender_status = 'Running'
else:
    sender_status = 'Not Running %s' % h.link_to_remote('Start', dict(
            update='senderStatus',
            url=h.url_for(controller='admin', action='restart_sender')
        ))
%>
Sender: 
${sender_status}

