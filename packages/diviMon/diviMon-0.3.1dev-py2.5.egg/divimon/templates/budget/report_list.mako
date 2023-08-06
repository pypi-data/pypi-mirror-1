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
Budgets = model.Session.query(model.Budget)
%>


%for budget in Budgets:
    ${budget.month}
%endfor



%for budget in Budgets:
<td><li>
<ul>
    Weekly Budget ${budget.budget}
</ul>
<ul>
    <%
    from divimon import model
    BudgetExpenses = model.Session.query(model.BudgetExpense).filter_by(budget=budget.id)
    beg_budget = 0
    cumulative_budget = int(budget.budget) # beg_budget + budget.budget
    %>
    %for bexpense in BudgetExpenses:
        <br>Expense ${bexpense.expense}
        <%
        from divimon import model
        Expenses = model.Session.query(model.Expense).filter_by(id=bexpense.expense).filter_by(area=1)
        total_expense = 0
        %>
        %for expense in Expenses:
            <%
            total_expense += int(expense.release)
            total_expense -= int(expense.returns)

            from divimon import model
            TransExpenses = model.Session.query(model.TransExpense).filter_by(expense=expense.id)
            %>
            <br>
            Expense cost
            ${total_expense}
            %for texpense in TransExpenses:
                <br>
                DR ${texpense.transaction}
            %endfor
        %endfor
            <br>
            <%
            cumulative_budget -= total_expense
            %>
        Cumulative Budget - ${cumulative_budget}


        <br>
    %endfor
</ul>
</li></td>


%endfor






</div>

