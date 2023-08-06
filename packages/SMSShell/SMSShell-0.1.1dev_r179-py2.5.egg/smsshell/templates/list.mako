<%doc>
list.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17
    2008-03-18

</%doc>
<%inherit file="list_base.mako"/>

<% c_count = len(c.columns) + 1 %>

<div id="list-page">
<h1>${c.title}</h1>

${self.show_table(c.table, c.columns, c.entries)}

</div>

