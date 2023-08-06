<%doc>
edit.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/edit_base.mako"/>

<h1>${c.title}</h1>

<form name="editForm" action="save" method="">
% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
<dl>

<% col = 'keyword' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

<% col = 'table' %>
<dt>${col}</dt>
<dd>
<%
    value = getattr(c.entry, col)
    tables = c.custom_tables.keys()
    tables.insert(0, '')
    options = h.options_for_select(tables, value)
%>
${h.select(col, options)}
</dd>

<% col = 'action' %>
<dt>${col}</dt>
<dd>
<%
    value = getattr(c.entry, col)
    options = h.options_for_select(['', 'show', 'add'], value)
%>
${h.select(col, options)}
</dd>

<% col = 'active' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

<% col = 'comment' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

${self.show_properties()}

${self.show_children()}

</dl>

<input type="submit" value="Save" />

</form>


