<%
label = "label-%s" % c.id
next = str(int(c.id)+1)
next_label = "label-%s" % str(next)
prev = str(int(c.id)-1)
prev_label = "label-%s" % str(prev)

rem_link = h.link_to_remote("remove",
        dict(update=prev_label,
            url=h.url_for(action='remove_label', id=prev)
    ))
add_link = h.link_to_remote("add",
        dict(update=label,
            url=h.url_for(action='add_label', id=c.id)
    ))
%>
%if int(c.id) > 1:
    ${rem_link}
%endif
${add_link}
