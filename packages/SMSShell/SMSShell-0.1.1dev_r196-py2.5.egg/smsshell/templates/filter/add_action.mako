<%doc>
</%doc>

<%inherit file="/add_child_base.mako"/>

% for col in c.columns:
    % if col != 'id':
    <td>
    <%
        input = self.show_field(col)
    %>
    ${input}
    </td>
    % endif
% endfor
<td class="child-remove-link">
${h.link_to_remote("remove",
        dict(update='new-'+c.child+'-'+c.cnt, url=h.url_for(action='blank_out'))
    )}
</td>

