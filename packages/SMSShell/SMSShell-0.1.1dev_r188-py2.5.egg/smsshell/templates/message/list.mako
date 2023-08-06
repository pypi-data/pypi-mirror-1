<%doc>
list.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17
    2008-03-18

</%doc>
<%inherit file="/list_base.mako"/>

<%
%>

<%def name="show_table_entry_functions(entry)">
    <% function='details' %>
    %if function in c.entry_functions:
    <a href="${function}?id=${entry.id}" title="${function}"
        ><img src="${g.base_url}/icons/${function}.png" alt="${function}" class="function-image" /></a>
    %endif
    <% function='edit' %>
    %if function in c.entry_functions:
    <a href="${function}?id=${entry.id}" title="${function}"
        ><img src="${g.base_url}/icons/${function}.png" alt="${function}" class="function-image" /></a>
    %endif
    <% function='delete' %>
    %if function in c.entry_functions:
    <a onclick="return areyousure('You sure you want to delete this entry?')"
        href="${function}?id=${entry.id}" title="${function}"
        ><img src="${g.base_url}/icons/${function}.png" alt="${function}" class="function-image" /></a>
    %endif
    <%
    function='reply'
    try:
        label = request.params['show_label']
    except KeyError:
        label = ''
    %>
    <a href="${function}?id=${entry.id}&amp;show_label=${label}" title="${function}"
        ><img src="${g.base_url}/icons/${function}.png" alt="${function}" class="function-image" /></a>
</%def>

<%def name="show_table_label_functions()">
    <span class="function">
    <input name="function" type="submit"
        onclick="this.value='Add Label';"
        value="Add" />
    <input name="function" type="submit"
        onclick="this.value='Remove Label';"
        value="Remove" />
    <strong>Label</strong>
    <!--select name="label" onchange="this.form.function.value='label'; this.form.submit();"-->
    <select name="label">
    <option></option>
    %for label in c.labels:
        <option value="${label.id}">${label.name}</option>
    %endfor
    </select>
    </span>
</%def>

<%def name="show_table_functions_custom()">
${self.show_table_label_functions()}
</%def>

<%def name="show_table_functions()">
    %if 'delete' in c.list_functions:
    <span class="function">
        <input onclick="return areyousure('You sure you want to delete these entries?');"
            name="function" type="submit" value="${g.function_delete}" />
    </span>
    %endif
    %if 'add' in c.list_functions:
    <span class="function">
        <a href="add" title="Create new entry">New</a>
    </span>
    %endif

    ${self.show_table_functions_custom()}

    ${self.show_table_pagination()}
</%def>

<%def name="show_table_head(columns)">
    <input type="hidden" name="show_label"
        value="${request.params.get('show_label', '')}" />
    <thead>
    <tr>
    <%
    c.columns_additional += 1
    c_count = len(columns) + c.columns_additional
    %>
    <td colspan="${c_count}">
    ${self.show_table_functions()}
    </td>
    </tr>
    <tr>
    <th width="12px">
        <input name="select_all"
            onchange="return check_all(this.checked, this.form.select);"
            type="checkbox" />
    </th>
    <th>
    </th>
    %for col in columns:
    <th>
        %if col in c.column_descriptions.keys():
            ${c.column_descriptions[col]}
        %else:
            ${col}
        %endif
    </th>
    %endfor
    <th>Labels</th>
    </tr>
    </thead>
</%def>

<%def name="show_table_entry(entry, columns)">
    <td>
        <input name="select" value="${entry.id}" id="select-${entry.id}"
            %if str(entry.id) in request.params.dict_of_lists().get('select', []):
                checked="checked"
            %endif
            type="checkbox" />
    </td>
    <th class="crud">${self.show_table_entry_functions(entry)}</th>
    % for col in columns:
    <td>
        ${self.get_value(entry, col)}
    </td>
    % endfor
    <td>
        ${', '.join(label.name for label in entry.label)}
    </td>
</%def>

<div id="list-page">
<h1>${c.title}</h1>

${self.show_table(c.table, c.columns, c.entries)}

</div>

