<%doc>
</%doc>

<%
%>


<ul>
%for phone in c.phones:
    <%
    if phone.contact is None:
        continue
    name = c.contacts.get(phone.contact).name
    %>
    <li>
    <a href="#"
    %if phone.number[-10:] in c.selected:
        style="background-color: #95e0c8;"
    %endif
    onclick="add_rem(this, document.getElementById('recipient'), '${phone.number}');">
    ${name}
    (${phone.number})
    </a>
    </li>
%endfor
</ul>

