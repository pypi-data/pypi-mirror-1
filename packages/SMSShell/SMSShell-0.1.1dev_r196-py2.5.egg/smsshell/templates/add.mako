<%inherit file="edit_base.mako"/>

<h1>Edit</h1>

ID: ${c.id}
<%
type = c.table.c.id.type
%>
<!--
${type}
${dir(type)}
-->

<form action="" method="">
<dl>
% for col in c.columns:
    % if col != 'id':
    <dt>${col}</dt>
    <%
        input = self.get_input(col)
        type = getattr(c.table.c, col).type
    %>
    <dd>${input}<!-- (${type}:${dir(type)})--></dd>
    % endif
% endfor
</dl>
<input type="submit" value="Save" />

</form>


