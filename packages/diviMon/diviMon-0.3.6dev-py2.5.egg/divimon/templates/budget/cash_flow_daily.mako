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



print c
start_day = datetime.now().day
end_day = datetime.now().day
start_month = datetime.now().month
end_month = datetime.now().month
start_year = datetime.now().year
end_year = datetime.now().year

start_day = int(c.start_day)
end_day = int(c.end_day)
start_month = int(c.start_month)
end_month = int(c.end_month)
start_year = int(c.year)
end_year = int(c.year)

beg_date = datetime(start_year, start_month, start_day, 0, 0)
end_date = datetime(end_year, end_month, end_day, 23, 59)
print beg_date
print end_date


months = ['','January','February','March','April','May','June','July','August','September','October','November','December']
from divimon import model
Sales = model.Session.query(model.Transaction).filter(model.Transaction.created<=end_date).filter(model.Transaction.created>=beg_date)
Sales_on_cheque = Sales.filter_by(pay_type=3)
Cheques = model.Session.query(model.Cheque)
Expenses = model.Session.query(model.Expense).filter(model.Expense.created<=end_date).filter(model.Expense.created>=beg_date)

total_markup = 0
markup = 0
total_cost_on_goods = 0
total_sales = 0
total_unearned = 0
total_earned = 0
total_cost_on_sold = 0
total_expense = 0

for sale in Sales:
    total_sales += float(sale.total_price)
total_unearned = 0

for sale_cheque in Sales_on_cheque:
    Cheque = Cheques.filter_by(dr=sale_cheque.id)
    if Cheque[0].status != 2:
        total_unearned += float(Cheque[0].amount)

for expense in Expenses:
    total_expense += expense.release - expense.returns


for sale in Sales:
    from divimon import model
    TransItems = model.Session.query(model.TransItem).filter_by(transaction=sale.id)
    beg_sale = 0
    total_purchase_price = 0
    for titem in TransItems:
        from divimon import model
        Item = model.Session.query(model.Item).filter_by(id=titem.item)
        total_purchase_price += float(Item[0].purchase_price) * float(titem.qty)
        total_cost_on_goods += total_purchase_price
        markup = float(sale.total_price) - float(total_purchase_price)
        markup_display = markup
        if markup < 0:
            markup_display = float(markup * -1)
        total_markup += markup
endfor

Income = total_sales - total_cost_on_goods - total_expense
Income_less_unearned = Income - total_unearned
%>
During the month of ${months[start_month]} ${now.year}
<br><br>
<div>
<table>

${beg_date}
${end_date}
<tr>
<ul>
    <td>
        <tr>
            <td>Total Sales</td>
            <td>&nbsp - &nbsp</td>
            <td></td>
            <td></td>
            <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
            <td style="text-align: right;">${g.currency(total_sales)}</td>
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
        <td style="text-align: right;">${g.currency(total_cost_on_goods)}</td>
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
        <td style="text-align: right;">${g.currency(total_expense)}</td>
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
        <td style="border:1px solid #963332;text-align: right;">${g.currency(Income * -1)}</td>
        <td></td>
        <td></td>
%else:
        <td></td>
        <td></td>
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="border:1px solid #828633;text-align: right;">${g.currency(Income)}</td>
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
        <td style="text-align: right;">${g.currency(total_unearned)}</td>
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
        <td style="border:1px solid #963333;text-align: right;">${g.currency(Income_less_unearned * -1)}</td>
        <td></td>
        <td></td>
%else:
        <td></td>
        <td></td>
        <td>&nbsp;&nbsp;P&nbsp;&nbsp;</td>
        <td style="border:1px solid #828633;text-align: right;">${g.currency(Income_less_unearned)}</td>
%endif
        </tr>
    </td>
</ul>


</table>
</div>

<br><br><br>
<form name="editForm" action="previous" method="">
<input type="hidden" name="start_day" value=${start_day} />
<input type="hidden" name="end_day" value=${end_day} />
<input type="hidden" name="start_month" value=${start_month} />
<input type="hidden" name="end_month" value=${end_month} />
<input type="hidden" name="start_year" value=${start_year} />
<input type="hidden" name="end_year" value=${end_year} />
<input type="submit" value="< Previous day" />

</div>

