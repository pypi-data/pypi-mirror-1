<%doc>
daily_markup.mako - Template for DiviMon application

AUTHOR: Erwin Pacheco <erwin.pacheco@gmail.com>

Modification Dates:
    2008-07-23

</%doc>
<%inherit file="/report_list_base.mako"/>

<% c_count = len(c.columns) + 1 %>

<div id="list-page">
<h1>${c.title} Report</h1>

<%
from datetime import datetime,timedelta
now = datetime.now()
today = datetime(now.year, now.month, now.day, 0, 0)
tomorrow = today + timedelta(1)
cur_month = datetime.now().month
beg_day = datetime(now.year, now.month, 1, 0, 0)
end_day = datetime(now.year, now.month, 31, 23, 59)
months = ['','January','February','March','April','May','June','July','August','September','October','November','December']
from divimon import model
Sales = model.Session.query(model.Transaction).filter(model.Transaction.created<end_day).filter(model.Transaction.created>=beg_day)
total_markup = 0
markup = 0
%>

During the month of ${months[now.month]} ${now.year}
<br><br>
<div>
<table>

%for sale in Sales:
<tr>
<ul>
    <td>
        <tr>
            <td>DR  ${sale.id} &nbsp ${sale.created.month}/${sale.created.day}/${sale.created.year} </td>
            <td>&nbsp - &nbsp</td>
            <td></td>
            <td></td>
            <td>&nbsp;&nbsp;&nbsp;P</td>
            <td>${sale.total_price.__float__()}</td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
            <td>
    <%
    from divimon import model
    TransItems = model.Session.query(model.TransItem).filter_by(transaction=sale.id)
    beg_sale = 0
    total_orig_price = 0
    %>
    Items: <br>
    %for titem in TransItems:
        <%
        from divimon import model
        Item = model.Session.query(model.Item).filter_by(id=titem.item)
        total_orig_price += float(Item[0].price) * float(titem.qty)
        %>
        ${Item[0].name} ${titem.qty} ${Item[0].unit}s<br>
    %endfor
        </td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        
        <td>Cost of goods sold </td>
        <td>&nbsp - &nbsp</td>
        <td>&nbsp;&nbsp;&nbsp;P</td>
        <td>${total_orig_price.__float__()}</td>
        <td></td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        <td></td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td>___</td>
        <td>______________</td>
        <td>&nbsp;&nbsp;___</td>
        <td>______________</td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        <td>Mark-up</td>
        <td>&nbsp - &nbsp</td>
        <%
        markup = float(sale.total_price) - float(total_orig_price)
        markup_display = markup
        if markup < 0:
            markup_display = float(markup.__float__ * -1)
        total_markup += markup
        %>
        <td></td>
        <td></td>
        <td>&nbsp;&nbsp;&nbsp;P</td>
        <td style="border:1px solid #828633;">${markup_display}</td>
        </tr>
    </td>
</ul>
<ul>
<td><br><br><br></td>
</ul>
</tr>

%endfor

<ul>
    <td>
        <tr>
        <td> Month Total Markup: </td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td></td>
        <td></td>
        <td>&nbsp;&nbsp;&nbsp;P</td>
        <td style="border:2px solid #828633;">${total_markup}</td>
        </tr>
    </td>
</ul>

</table>
</div>

</div>

