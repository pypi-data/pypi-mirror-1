

<dl>

<dt>Name:</dt>
<dd>${c.entry.name}</dd>

<dt>Address:</dt>
<dd>${c.entry.address}</dd>

<dt>Area:</dt>
<%
from divimon import model
entry = model.list(c.parent['area']['table']).get(c.entry.area)
value = getattr(entry, c.parent['area']['column'])
%>
<dd>${value}</dd>

<dt>Created:</dt>
<dd>${c.entry.created}</dd>

</dl>

