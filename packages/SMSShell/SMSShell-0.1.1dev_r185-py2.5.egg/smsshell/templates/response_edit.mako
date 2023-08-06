<%doc>
edit.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="edit_base.mako"/>

<h1>${c.title}</h1>

<%
from smsshell import model
from sqlalchemy.schema import Table
%>

<form action="save" method="">
% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
<dl>

<% col = 'keyword' %>
<dt>${col}</dt>
<dd>${self.show_field(col)}</dd>

<% col = 'table' %>
<dt>${col}</dt>
<dd>
    <select name="${col}">
    <option></option>
    %for tbl in dir(model):
    %if hasattr(getattr(model, tbl), 'id'):
        %if c.entry.table == tbl:
            <option selected="selected">${tbl}</option>
        %else:
            <option>${tbl}</option>
        %endif
    %endif
    %endfor
    </select>
</dd>

<% col = 'action' %>
<dt>${col}</dt>
<dd>
    <select name="${col}">
    <option></option>
    ##%for action in ('search', 'add', 'edit', 'delete', 'show'):
    %for action in ('search', 'edit', 'delete', 'show'):
    %if c.entry.action == action:
        <option selected="selected">${action}</option>
    %else:
        <option>${action}</option>
    %endif
    %endfor
    </select>
</dd>

</dl>

<h3>Arguments</h3>
<%
children_entries = getattr(c.entry, 'argument')
children = {}
for entry in children_entries:
    children[entry.priority] = (entry.id, entry.field)
%>
<ol>
%for cnt in range(1, 11):
<%
id_val = ''
field_val = ''
if cnt in children.keys():
    id_val = children[cnt][0]
    field_val = children[cnt][1]
%>
<li>
<input type="hidden" name="id-${cnt}" value="${id_val}" />
<input name="field-${cnt}" value="${field_val}" />
</li>
%endfor
</ol>

<input type="submit" value="Save" />

</form>


