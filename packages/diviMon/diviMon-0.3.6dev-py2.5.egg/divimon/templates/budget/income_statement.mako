<%doc>
report_list.mako - Template for SMSShell application

AUTHOR: Erwin Pacheco <erwin.pacheco@gmail.com>

Modification Dates:
    2008-07-08

</%doc>
<%inherit file="/report_list_base.mako"/>

<% c_count = len(c.columns) + 1 %>

<div id="list-page">
<h1>${c.title} Report</h1>

<%
from datetime import datetime
now = datetime.now()

from divimon import model
Sales = model.Session.query(model.Transaction)
Expenses = model.Session.query(model.Expense)
%>

Sales Income Statement

%for expense in Expenses:
<td><li>
<ul>
Budget for ${expense.created}
</ul>
<ul>
    <%
    from datetime import datetime,timedelta
    from divimon import model
    TransExpenses = model.Session.query(model.TransExpense).filter_by(expense=expense.id)
    beg_expense = 0
    cumulative_expense = int(expense.release) - int(expense.returns)  # beg_expense + expense.cost
    now = datetime.now()
    today = datetime(now.year, now.month, now.day, 0, 0)
    tomorrow = today + timedelta(1)
    %>
    %for texpense in TransExpenses:
        <br>Delivery reciept ${texpense.transaction}
        <%
        from divimon import model
        Transactions = model.Session.query(model.Transaction).filter(self.table.c.created<tomorrow).filter(self.table.c.created>=today)

        total_expense = 0
        total_price = 0
        mark_up = 0
        expense_args = []
        %>
        %for tran in Transactions:
            <br>
            Transaction total price
            ${tran.total_price}
            <%
            total_price = int(tran.total_price)
            mark_up = int(tran.total_price)
            total_expense += int(expense.release) - int(expense.returns)

            from divimon import model
            TransItems = model.Session.query(model.TransItem).filter_by(transaction=tran.id)
            %>
            %for titem in TransItems:
                <br>
                Item ${titem.item} price ${titem.price}
                <%mark_up -= titem.price%>
            %endfor
        %endfor
        <br>
        Transaction Mark-up  ${mark_up}
        <br>
            <%
            cumulative_expense -= total_expense
            %>
        Cumulative Budget - ${cumulative_expense}


        <br>
    %endfor
</ul>
<ul>
<%
expenses = expense.release - expense.returns
%>
    <td><span><br>Expenses </span><span> ${expenses}</span></td>
    <br>(fuel, meal, toll fee, miscellaneous)
</ul>
</li></td>


%endfor






</div>

