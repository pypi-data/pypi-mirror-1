<%doc>
list.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17
    2008-03-18

</%doc>
<%inherit file="/message/list.mako"/>

<%
%>

<%def name="show_table_functions_custom()">
    ${self.show_table_label_functions()}
    <span class="function">
    <input name="function" type="submit" value="Archive" />
    </span>
</%def>

<div id="list-page">
<h1>${c.title}</h1>

${self.show_table(c.table, c.columns, c.entries)}

</div>

