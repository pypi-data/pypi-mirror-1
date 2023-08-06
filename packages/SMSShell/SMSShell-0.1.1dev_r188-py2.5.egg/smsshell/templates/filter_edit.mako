<%doc>
edit.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="edit_base.mako"/>

<%
from smsshell import model
%>

<script language="javascript" type="text/javascript">
<!--

var num;

function add_label(num) {
}

//-->
</script>

<h1>${c.title}</h1>

<form action="save" method="">
% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
<dl>
%for col in c.columns:
    % if col != 'id':
    <dt>${col}</dt>
    <dd>
    <%
        input = self.show_field(col)
        type = getattr(c.table.c, col).type
    %>
    ${input}
    </dd>
    % endif
%endfor


</dl>

##<div id="label-1">
##${h.link_to_remote("add", dict(update="label-1", url=h.url_for(action='add_label', id=1)))}
##</div>


<input type="submit" value="Save" />

</form>


