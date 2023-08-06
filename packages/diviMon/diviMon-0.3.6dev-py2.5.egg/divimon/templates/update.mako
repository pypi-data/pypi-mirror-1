<%doc>
blank.mako - Blank Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-04-03

</%doc>
<%inherit file="base.mako"/>

<%
%>

<h1>Remote Commit / Update</h1>

<form>
<dl>
    <dt>
    Table
    </dt>
    <dd>
    <select name="table">
    % for table in ('User', 'Item', 'Inventory', 'Agent', 'Customer', 'Cheque', 'DeliveryReceipt', 'Budget', 'Expense', ):
        <option value="${table}">${table}</option>
    % endfor
    </select>
    </dd>
    <dt>
    &nbsp;
    </dt>
    <dd>
    <input type="submit" name="action" value="update">
    <input type="submit" name="action" value="commit">
    </dd>
</dl>
</form>

