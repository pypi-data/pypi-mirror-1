
<%
from datetime import datetime
now = datetime.now()
%>

<%def name="get_value(entry, col)">
<%
from sqlalchemy import types
table = entry.__class__
tbl_col = getattr(table.c, col)
value = getattr(entry, col)
if value is None:
    value = ''
elif len(tbl_col.foreign_keys) > 0:
    v_id = getattr(entry, col)
    table = c.parent[col]['table']
    entry = c.db_sess.query(table).get(v_id)
    value = getattr(entry, c.parent[col]['column'])
elif isinstance(tbl_col.type, types.DateTime):
    from datetime import datetime
    now = datetime.now()
    v = getattr(entry, col)
    if v <= now:
        value = '%s ago' % h.date.time_ago_in_words(v)
    else:
        value = '%s from now' % h.date.time_ago_in_words(v)
    '''
    date_diff = now.date() - v.date()
    date_diff = date_diff.days
    if date_diff == 0:
        value = v.strftime('%H:%M')
    elif date_diff == 1:
        value = 'Yesterday ' + v.strftime('%H:%M')
    elif date_diff < 7:
        value = v.strftime('%a %H:%M')
    elif now.year == v.year:
        value = v.strftime('%b %d')
    else:
        value = v.strftime('%Y %b %d')
    '''
    value = '<span style="text-transform: capitalize;">%s</span>' % value
else:
    value = getattr(entry, col)
if value is None:
    value = ''
%>
${value}
</%def>


