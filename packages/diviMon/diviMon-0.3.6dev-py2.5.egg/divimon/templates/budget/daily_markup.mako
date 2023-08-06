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
            <td></td>
            <td></td>
            <td></td>
            <td>P</td>
            <td align='right' >${g.currency(sale.total_price)}</td>
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
        total_orig_price += float(Item[0].purchase_price) * float(titem.qty)
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
        <td>Cost on goods sold </td>
        <td></td>
        <td>P</td>
        <td align='right' >${g.currency(total_orig_price)}</td>
        <td></td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        <td>Mark-up</td>
        <td></td>
        <%
        markup = float(sale.total_price) - float(total_orig_price)
        markup_display = markup
        total_markup += markup
        %>
        % if markup < 0:
        <%    markup *= -1   %>
        <td style="border-top:1px solid;">P</td>
        <td align='right' style="border-top:1px solid;">${g.currency(markup)}</td>
        <td style="border-top:1px solid;"></td>
        <td style="border-top:1px solid;"></td>
        % else:
        <%    markup_display = float(markup)   %>
        <td style="border-top:1px solid;"></td>
        <td style="border-top:1px solid;"></td>
        <td style="border-top:1px solid;">P</td>
        <td align='right' style="border-top:1px solid;">${g.currency(markup)}</td>
        % endif
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
        % if total_markup < 0:
        <%  total_markup *= -1  %>
        <td>P</td>
        <td  align='right' style="border:1px solid #828633;">${g.currency(total_markup)}</td>
        <td></td>
        <td></td>
        % else:
        <td></td>
        <td></td>
        <td>P</td>
        <td  align='right' style="border:1px solid #828633;">${g.currency(total_markup)}</td>
        % endif
        </tr>
    </td>
</ul>

</table>
</div>

</div>

