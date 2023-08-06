<%
label = "label-%s" % c.id
next = str(int(c.id)+1)
next_label = "label-%s" % str(next)
prev = str(int(c.id)-1)
prev_label = "label-%s" % str(prev)

rem_link = h.link_to_remote("remove",
        dict(update=label,
            url=h.url_for(action='remove_label', id=c.id)
    ))
add_link = h.link_to_remote("add",
        dict(update=next_label,
            url=h.url_for(action='add_label', id=next)
    ))
%>
    <select name="label">
    <option></option>
    %for label in c.labels:
        <option value="${label.id}">${label.name}</option>
    %endfor
    </select>

<div id="${next_label}">
${rem_link}
${add_link}
</div>
