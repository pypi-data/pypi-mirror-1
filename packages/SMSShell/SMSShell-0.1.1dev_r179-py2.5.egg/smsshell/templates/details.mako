<%doc>
details.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="details_base.mako"/>
<%inherit file="list_base.mako"/>

<h1>${c.title}</h1>

<dl>
% for col in c.columns:
    % if col != 'id':
    <dt>${col}</dt>
    <dd>${self.get_value(c.entry, col)}</dd>
    % endif
% endfor
</dl>

% if len(c.properties) > 0:
<h2>Properties</h2>
##Show Properties
<dl>
% for prop in c.properties:
    <%
        column = prop[0]
        prop_col = prop[1]
        properties = getattr(c.entry, column)
    %>
    <dt>${column}</dt>
    <dd>
    % for property in properties:
        ${getattr(property, prop_col)}
    % endfor
    </dd>
% endfor
</dl>
% endif

% if False and len(c.children) > 0:
<h2>Children</h2>
##Show Children
<dl>
% for column, child_details in c.children.iteritems():
    <dt>${column}</dt>
    <dd>
    <%
    child_tbl = child_details['table']
    child_cols = child_details['columns']
    children = getattr(c.entry, column)
    c.list_functions = []
    c.entry_functions = []
    %>
    ${self.show_table(child_tbl, child_cols, children)}
    </dd>
% endfor
</dl>
% endif


