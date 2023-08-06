<%doc>
edit.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/edit_base.mako"/>

<%
%>

<h1>${c.title}</h1>

<form name="editForm" action="save" method="">
% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
<input type="hidden" name="folder" value="3" />
<input type="hidden" name="sender" value="${g.number}" />
%if 'show_label' in request.params:
    <input type="hidden" name="show_label" value="${request.params['show_label']}" />
% endif
<dl>

<% col='recipient' %>
<dt>${c.column_descriptions.get(col, col)}</dt>
<dd>
<script src="${g.base_url}/js/show_contacts.js" language="javascript" type="text/javascript"></script>
<div id="recipientField">
    <%
    value = getattr(c.entry, 'recipient')
    if value is None:
        value = ''
    %>
    <input id="recipient" name="recipient"
        onkeydown="show_contacts(this);"
        onkeyup="show_contacts(this);"
        onchange="show_contacts(this);"
        value="${value}" />
    <small>(space-separated)</small>
    <div id="contactList">
    <a href="#" onclick="show_contacts(document.getElementById('recipient'))">Show Contacts</a>
    </div>
</div>
</dd>

<% col='message' %>
<dt>${c.column_descriptions.get(col, col)}</dt>
<dd>${self.show_field(col)}</dd>

<% col='created' %>
<dt>Schedule</dt>
<dd>${self.show_field(col)}</dd>

</dl>
<input type="submit" value="Send" />

</form>


