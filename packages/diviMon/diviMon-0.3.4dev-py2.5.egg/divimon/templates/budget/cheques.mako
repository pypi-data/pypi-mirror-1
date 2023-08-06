<%doc>
daily_markup.mako - Template for DiviMon application

AUTHOR: Erwin Pacheco <erwin.pacheco@gmail.com>

Modification Dates:
    2008-07-23

</%doc>
<%inherit file="/report_list_base.mako"/>

<% c_count = len(c.columns) + 1 %>

<div id="list-page">
<h1>Cheque Amount by Status</h1>

<%
from datetime import datetime,timedelta
now = datetime.now()
today = datetime(now.year, now.month, now.day, 0, 0)
tomorrow = today + timedelta(1)
cur_month = datetime.now().month
beg_day = datetime(now.year, now.month, 1, 0, 0)
end_day = datetime(now.year, now.month, 31, 23, 59)
months = ['January','February','March','April','May','June','July','August','September','October','November','December']
from divimon import model
Sales = model.Session.query(model.Transaction).filter(model.Transaction.created<=end_day).filter(model.Transaction.created>=beg_day)
Sales_on_cheque = Sales.filter_by(pay_type=3)
Cheques = model.Session.query(model.Cheque).filter(model.Transaction.created>=beg_day)
print Sales_on_cheque
total_cost_on_goods = 0
total_sales = 0

total_claimed = 0
total_for_claiming = 0
total_for_return = 0
total_returned = 0

total_earned = 0
total_cost_on_sold = 0
total_expense = 0

total_a = 0

cheque_list_month = list()

for sale in Sales:
    print sale
    print sale.pay_type


total_for_claiming = 0

for sale_cheque in Sales_on_cheque:
    Cheque = Cheques.filter_by(dr=sale_cheque.id)
    cheque_list_month.append(Cheque[0])
    if Cheque[0].status == 2:
        total_claimed += float(Cheque[0].amount)
    elif Cheque[0].status == 1:
        total_for_claiming += float(Cheque[0].amount)
    elif Cheque[0].status == 3:
        total_for_return += float(Cheque[0].amount)
    elif Cheque[0].status == 4:
        total_returned += float(Cheque[0].amount)


%>
During the month of ${months[now.month]} ${now.year}
<br><br>
<div>
<table>


<tr>
</tr>

<ul>
    <td>
<br><br><br>
    </td>
</ul>

<ul>
    <td>
        <tr>
        <td>Total Claimed </td>
        <td>&nbsp - &nbsp</td>
        <td></td>
        <td></td>
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="text-align: right;">${total_claimed}</td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        <td>Total for Claiming </td>
        <td>&nbsp - &nbsp</td>
        <td>P</td>
        <td style="text-align: right;">${total_for_claiming}</td>
        <td></td>
        <td></td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        <td>Total for Returns </td>
        <td>&nbsp - &nbsp</td>
        <td></td>
        <td style="text-align: right;">${total_for_return}</td>
        <td></td>
        <td></td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        <td>Total Returned</td>
        <td>&nbsp - &nbsp</td>
        <td></td>
        <td style="text-align: right;">${total_returned}</td>
        <td></td>
        <td></td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        <td></td>
        <td></td>
        <td style="border-bottom:1px solid;"></td>
        <td style="border-bottom:1px solid;"></td>
        <td style="border-bottom:1px solid;"></td>
        <td style="border-bottom:1px solid;"></td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
<%total_a = total_claimed - (total_for_claiming + total_for_return + total_returned)%>
%if total_a > 0 :
        <td>Total Claimed</td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td></td>
        <td></td>
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="border:1px solid #828633;text-align: right;">${total_a}</td>
%else:
        <td>Total Unclaimed</td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="border:1px solid #963333;text-align: right;">${total_a * -1}</td>
        <td></td>
        <td></td>
%endif
        </tr>
    </td>
</ul>


</table>
</div>

</div>

