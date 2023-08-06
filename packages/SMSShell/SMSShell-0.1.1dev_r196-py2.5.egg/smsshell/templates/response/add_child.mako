<%doc>
</%doc>

<%inherit file="/add_child_base.mako"/>

<%def name="show_field_field(col)">
    <%
        #value = getattr(c.entry, col)
        value = ''
        columns = set([''])
        for table in c.custom_tables.values():
            for col in table.c.keys():
                columns.add(col)
        options = h.options_for_select(columns, value)
    %>
    ${h.select(col, options)}
</%def>

% for col in c.columns:
    % if col != 'id' and col != 'field':
    <td>
    <%
        input = self.show_field(col)
    %>
    ${input}
    </td>
    % elif col == 'field':
    <td>
        ${self.show_field_field(col)}
    </td>
    % endif
% endfor
<td class="child-remove-link">
${h.link_to_remote("remove",
        dict(update='new-'+c.child+'-'+c.cnt, url=h.url_for(action='blank_out'))
    )}
</td>

