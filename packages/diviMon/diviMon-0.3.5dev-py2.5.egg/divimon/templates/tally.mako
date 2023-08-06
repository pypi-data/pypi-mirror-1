<%doc>
tally.mako - Template for DiviMon application

AUTHOR: Erwin Pacheco <erwin.pacheco@gmail.com>

Modification Dates:
    2008-07-29

</%doc>
<%inherit file="/report_list_base.mako"/>

<% c_count = len(c.columns) + 1 %>

<div id="list-page">
<h1>Tally</h1>
<br><br>
<div>
<table>
<tr>

<%
from divimon import model
Items = model.Session.query(model.Item).order_by(model.Item.name.asc())
%>
%for item in Items:
<ul>
    <td>
        <tr>
            <td>${item.name}</td>

    

<%    Items_by_name = Items.filter_by(name=item.name)   %>

%    for item_by in Items_by_name:
        <% Inv_by_item = model.Session.query(model.Inventory).filter_by(item=item_by.id)    %>

            <td>&nbsp - &nbsp</td>
            <td>${Inv_by_item[0].qty}</td>

            <td>${item_by.unit}</td>
            <td></td>

    
%    endfor

        </tr>
    </td>
</ul>


%endfor
Current


</tr>



</table>
</div>

</div>

