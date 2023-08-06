<%doc>
</%doc>

<%
child = c.child
parent = c.parent
child_cnt = 0
%>

<h3>${child}</h3>
<table>
<thead>
<tr>
%for column in c.child_details['columns']:
    <th>
    ${column}
    </th>
%endfor
</tr>
</thead>
<tbody>
%for entry in c.children:
<%
child_cnt += 1
%>
<tr id="old-${child}-${child_cnt}">
%   for column in c.child_details['columns']:
    <td>
    ${getattr(entry, column)}
    </td>
%   endfor
<td>
<a href="#${child}" onclick="edit_child_${child}(${child_cnt}, ${entry.id}, ${c.parent.id});">edit</a>
</td>
</tr>
%endfor
%for cnt in range(1, 1+50):
    <tr id="new-${child}-${cnt}"></tr>
%endfor
</tbody>
</table>
<a href="#${child}" onclick="add_child_${child}();">add</a>
<a name="${child}">&nbsp;</a>

