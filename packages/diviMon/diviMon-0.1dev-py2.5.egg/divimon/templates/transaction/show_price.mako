<%doc>
</%doc>

<%
col = 'price'
%>
<input id="${col}-${c.cnt}" name="${c.child}.${col}"
    value="${"%0.2f" % c.price}"
    />

