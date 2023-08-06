<%doc>
daily_markup.mako - Template for DiviMon application

AUTHOR: Erwin Pacheco <erwin.pacheco@gmail.com>

Modification Dates:
    2008-07-23

</%doc>
<%inherit file="/report_list_base.mako"/>

<% c_count = len(c.columns) + 1 %>

<div id="list-page">
<h1>Cash Flow</h1>

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
Sales = model.Session.query(model.Transaction).filter(model.Transaction.created<=end_day).filter(model.Transaction.created>=beg_day)
Sales_on_cheque = Sales.filter_by(pay_type=3)
Cheques = model.Session.query(model.Cheque)
Expenses = model.Session.query(model.Expense).filter(model.Expense.created<=end_day).filter(model.Expense.created>=beg_day)
print Sales_on_cheque
total_markup = 0
markup = 0
total_cost_on_goods = 0
total_sales = 0
total_unearned = 0
total_earned = 0
total_cost_on_sold = 0
total_expense = 0

for sale in Sales:
    print sale
    total_sales += float(sale.total_price)
    print sale.pay_type
    #if sale.pay_type==3:
    #    Cheque = Cheques.filter_by(dr=sale.id)
    #    total_unearned += float(Cheque[0].amount)

print "Total Sales"
print total_sales
#print total_earned

total_unearned = 0
#print total_unearned

for sale_cheque in Sales_on_cheque:
    Cheque = Cheques.filter_by(dr=sale_cheque.id)
    if Cheque[0].status != 2:
        total_unearned += float(Cheque[0].amount)

print "Total Unearned Income"
print total_unearned

for expense in Expenses:
    total_expense += expense.release - expense.returns

print "Total Expense"
print total_expense

for sale in Sales:
    from divimon import model
    TransItems = model.Session.query(model.TransItem).filter_by(transaction=sale.id)
    beg_sale = 0
    total_orig_price = 0
    for titem in TransItems:
        from divimon import model
        Item = model.Session.query(model.Item).filter_by(id=titem.item)
        total_orig_price += float(Item[0].price) * float(titem.qty)
        total_cost_on_goods += total_orig_price
        markup = float(sale.total_price) - float(total_orig_price)
        markup_display = markup
        if markup < 0:
            markup_display = float(markup.__float__ * -1)
        total_markup += markup
endfor
print "Total Cost on Goods sold"
print total_cost_on_goods

Income = total_sales - total_cost_on_goods - total_expense
Income_less_unearned = Income - total_unearned

print "Income"
print Income
%>
During the month of ${months[now.month]} ${now.year}
<br><br>
<div>
<table>


<tr>
<ul>
    <td>
        <tr>
            <td>Total Sales</td>
            <td>&nbsp - &nbsp</td>
            <td></td>
            <td></td>
            <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
            <td style="text-align: right;">${total_sales.__float__()}</td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
            <td>

        </td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        <td>Cost on goods sold </td>
        <td>&nbsp - &nbsp</td>
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="text-align: right;">${total_cost_on_goods.__float__()}</td>
        <td></td>
        <td></td>
        </tr>
    </td>
</ul>
<ul>
    <td>
        <tr>
        <td>Total Expense (fuel, meal, toll fee, misc...)</td>
        <td>&nbsp - &nbsp</td>
        <td></td>
        <td style="text-align: right;">${total_expense.__float__()}</td>
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
        <td>Net Income</td>
        <td></td>
%if Income < 0:
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="border:1px solid #963332;text-align: right;">${Income.__float__() * -1}</td>
        <td></td>
        <td></td>
%else:
        <td></td>
        <td></td>
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="border:1px solid #828633;text-align: right;">${Income.__float__()}</td>
%endif
        </tr>
    </td>
</ul>
</tr>

<ul>
    <td>
<br><br><br>
    </td>
</ul>

<ul>
    <td>
        <tr>
        <td>Total Unearned Income (cheque payments)</td>
        <td>&nbsp - &nbsp</td>
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="text-align: right;">${total_unearned.__float__()}</td>
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
        <td>Current Income</td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>
%if Income_less_unearned < 0:
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="border:1px solid #963333;text-align: right;">${(float(Income_less_unearned) * -1).__float__()}</td>
        <td></td>
        <td></td>
%else:
        <td></td>
        <td></td>
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="border:1px solid #828633;text-align: right;">${Income_less_unearned.__float__()}</td>
%endif
        </tr>
    </td>
</ul>


</table>
</div>

</div>

