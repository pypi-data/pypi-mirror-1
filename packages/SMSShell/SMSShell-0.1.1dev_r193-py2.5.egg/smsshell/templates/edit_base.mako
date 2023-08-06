<%doc>
edit_base.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<% import re %>

<%inherit file="base.mako"/>

<%def name="get_type(col)">
    <%
    col_type = getattr(c.table.c, col).type
    if col_type:
        type = 'test'
    %>
</%def>

<%def name="show_field(col)">
    <%
    from sqlalchemy import types
    value = getattr(c.entry, col)
    if value is None:
        value = ''
    tbl_col = getattr(c.table.c, col)
    %>
    % if len(tbl_col.foreign_keys) > 0:
        ${self.show_field_select(col)}
    % elif isinstance(tbl_col.type, types.Boolean):
        <input type="checkbox"
            %if tbl_col.default.arg:
                checked="checked"
            %endif
            id="${col}" name="${col}" />
    % elif isinstance(tbl_col.type, (types.Text, types.UnicodeText)):
        <textarea id="${col}" name="${col}" cols="32" rows="6"
            onKeyDown="textCounter(this, document.editForm.${col}Len, 160)"
            onKeyUp="textCounter(this, document.editForm.${col}Len, 160)"
            >${value}</textarea>
        <small>
            Characters Left:
            <input readonly="readonly" name="${col}Len" value="160" size="3" />
        </small>
    % elif isinstance(tbl_col.type, types.Date):
        <input id="${col}" name="${col}" value="${value}" /><small>(YYYY-MM-DD)</small>
    % elif isinstance(tbl_col.type, types.DateTime):
        <input id="${col}" name="${col}" value="${value}" /><small>(YYYY-MM-DD HH:MM)</small>
    % elif isinstance(tbl_col.type, types.Time):
        <input id="${col}" name="${col}" value="${value}" /><small>(HH:MM)</small>
    % else:
        <input id="${col}" name="${col}" value="${value}" />
    % endif
</%def>

<%def name="show_field_select(col)">
    <%
    v_id = getattr(c.entry, col)
    p_table = c.parent[col]['table']
    p_column = c.parent[col]['column']
    p_entries = c.db_sess.query(p_table).select()
    %>
    <select id="${col}" name="${col}">
    %if getattr(c.table.c, col).nullable:
        <option value=""></option>
    %endif
    %for entry in p_entries:
        %if entry.id == v_id:
            <option value="${entry.id}" selected="selected">
                ${getattr(entry, p_column)}
            </option>
        %else:
            <option value="${entry.id}">
                ${getattr(entry, p_column)}
            </option>
        %endif
    %endfor
    </select>
</%def>

<%def name="show_properties()">
    %for prop in c.properties:
    <%
    from smsshell import model
    parent_field = prop[0]
    prop_field = prop[1]
    prop_table = prop[2]
    properties = getattr(c.entry, parent_field)
    prop_entries = model.list(prop_table)
    %>
    <dt>${parent_field}</dt>
    <dd>
        <select name="${parent_field}" multiple="multiple">
        %for prop in prop_entries:
            <option value="${prop.id}"
                %if prop in properties:
                    selected="selected"
                %endif
                >${getattr(prop, prop_field)}</option>
        %endfor
        </select>
    </dd>
    %endfor
</%def>

<%def name="show_children()">
    %for child in c.children:
    <script language="javascript" type="text/javascript">
    <!--
    var column;
    var ${child}_cnt=0;

    function add_child_${child}(child) {
        ${child}_cnt++;
        new Ajax.Updater('new-${child}-'+${child}_cnt, 'add_child?child=${child}&amp;cnt='+${child}_cnt, {asynchronous:true, evalScripts:true});
        //document.${child}-cnt.display: block;
        //return false;
    }

    function edit_child_${child}(cnt, id, p_id) {
        //${child}_cnt++;
        new Ajax.Updater('old-${child}-'+cnt, 'edit_child?c_id='+id+'&amp;p_id='+p_id+'&amp;child=${child}&amp;cnt='+cnt, {asynchronous:true, evalScripts:true});
        //document.${child}-cnt.display: block;
        //return false;
    }

    //-->
    </script>
    <%
    try:
        child_label = c.children[child]['label']
    except KeyError:
        child_label = child
    %>
    <div id="${child}-children" class="children">
    ${h.link_to_remote('Show '+child_label+' entries', dict(update=child+'-children', url=h.url_for(action='show_children', id=c.entry.id, child=child)))}
    </div>
    %endfor
</%def>

