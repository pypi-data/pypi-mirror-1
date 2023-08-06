<%doc>
base.mako - Base template for the SMSShell application

Modify this template if you want to change the overall look of the application.

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title> ${c.title} SMS Shell </title>
<link href="${g.base_url}/smsshell.css" type="text/css" rel="stylesheet" />
<script src="${g.base_url}/js/areyousure.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/list.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/show_hide.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/text_counter.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/server.js" language="javascript" type="text/javascript"></script>
${h.javascript_include_tag(builtins=True)}
</head>

<body>

<div id="topBar">

    <%
    from smsshell import model
    self.kwargs = {}
    for k,v in request.params.dict_of_lists().iteritems():
        if k == 'function':
            continue
        self.kwargs[k] = v
    %>
    %if g.debug:
    <div id="debug">
        <strong>Path:</strong>
        ${request.host}
        ${h.url_for()}
        ?${h.cgi_for(**self.kwargs)}
    </div>
    %endif

    <%
    import commands
    %>

    <div class="status" id="senderStatus">
    <%
    link = h.link_to_remote('Start', dict(
            update='senderStatus',
            url=h.url_for(controller='admin', action='restart_sender')
        ))
    link = '<a href="#" onclick="startSender();">Start</a>'
    output = commands.getoutput('ps ax | grep sender')
    if output.find('sender.py') > -1 and output.find('python') > -1:
        sender_status = 'Running'
    else:
        sender_status = 'Not Running %s' % link
    %>
    Sender: 
    ${sender_status}
    </div>

    <div class="status" id="receiverStatus">
    <%
    link = h.link_to_remote('Start', dict(
            update='receiverStatus',
            url=h.url_for(controller='admin', action='restart_receiver')
        ))
    link = '<a href="#" onclick="startReceiver();">Start</a>'
    output = commands.getoutput('ps ax | grep box')
    if output.find('smsbox') > -1 and output.find('bearerbox') > -1:
        receiver_status = 'Running'
    else:
        receiver_status = 'Not Running %s' % link
    %>
    Receiver: 
    ${receiver_status}
    </div>

</div>

<div id="sidebar">

<div id="title">
    <h1>
    <a href="${g.base_url}/"><img src="${g.base_url}/img/logo.png" alt="SMS Shell" style="border: none;" /></a>
    </h1>
</div>

<div id="menu">

    <div>
    <ul>

    <li class="menuTop">
    <a href="#" onclick="show_hide('menuMessage');">Messages</a>
        <ul id="menuMessage">
        <li><a href="${g.base_url}/outbox/add" title="Create New Message">Compose</a></li>
        <li><a href="${g.base_url}/inbox/" title="Recently received messages">Inbox</a></li>
        <li><a href="${g.base_url}/outbox/" title="Messages to be Sent">Outbox</a></li>
        <li><a href="${g.base_url}/sent/" title="Sent Messages">Sent</a></li>
        <li><a href="${g.base_url}/archive/" title="Archived Messages">Archive</a></li>
        </ul>
    </li>

    </ul>
    </div>

    <div>
    <ul>

    <li class="menuTop">
    <a href="#" onclick="show_hide('menuLabel');" title="Message Labels">Labels</a>
        <ul id="menuLabel">
        <li class="smallLink">
            <a href="${g.base_url}/label/" title="Edit Labels">Edit Labels</a>
        </li>
        %for label in model.list(model.Label).order_by(model.Label.c.name):
            <li><a href="${g.base_url}/message/?show_label=${label.id}"
                title="Messages labelled ${label.name}">${label.name}</a></li>
        %endfor
        </ul>
    </li>

    </ul>
    </div>

    <div>
    <ul>

    <li class="menuTop">
    <a href="${g.base_url}/contact/" title="List of Contacts">Contacts</a>
    </li>

    <!--
    <li>
    <a href="${g.base_url}/estate/" title="Estates">Estates</a>
    </li>
    -->

    <li>
    <a href="${g.base_url}/filter/" title="Message Filters">Filters</a>
    </li>

    <li>
    <a href="${g.base_url}/response/" title="Programmed Response">Response</a>
    </li>

    </ul>
    </div>

</div>

</div>

<div id="main">
## ${self.body()}
## ${next.body()}
${self.body()}
</div>

<div id="footer">
<p>Copyright &copy; Emanuel Gardaya Calso</p>
</div>

</body>

</html>
