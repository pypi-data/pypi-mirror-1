<%doc>
base.mako - Base template for the SMSShell application

Modify this template if you want to change the overall look of the application.

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html>
<head>
<title> ${c.title} POS </title>
<meta http-equiv="pragma" content="no-cache">
<link href="${g.base_url}/smsshell.css" type="text/css" rel="stylesheet" />
<link href="${g.base_url}/hh.css" type="text/css" rel="stylesheet" />
<script src="${g.base_url}/js/areyousure.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/list.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/show_hide.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/text_counter.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/server.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/date_chooser/date-functions.js" type="text/javascript"></script>
<script src="${g.base_url}/date_chooser/datechooser.js" type="text/javascript"></script>
<!-- <script src="${g.base_url}/javascript/edit.js" type="text/javascript"></script> -->
<link href="${g.base_url}/date_chooser/datechooser.css" rel="stylesheet" type="text/css" />
${h.javascript_include_tag(builtins=True)}
</head>

<body>

<div id="topBar">


</div>

<div id="sidebar">

<div id="title">
    <h1>
    <a href="${g.base_url}/">POS</a>
    </h1>
</div>

<div id="menu">

    <div>
    <ul>
        <li class="menuTop">Front End</li>
        <li><a href="${g.base_url}/delivery_receipt/" title="List of Receipt Sale Deliveries">Delivery Receipt</a></li>
        <li><a href="${g.base_url}/expense/" title="List of Daily Budget Release">Budget - Daily Release</a></li>
        <li><a href="${g.base_url}/budget/" title="List of Weekly Budget Allotment">Budget - Weekly Allotment</a></li>
        <li>Stocks</li>
        <li><a href="${g.base_url}/inventory/" title="Inventory">Inventory</a></li>
        <li><a href="${g.base_url}/stocks_out/" title="Stocks Out">Stocks Out</a></li>
        <li><a href="${g.base_url}/item/tally" title="Tally Sheet of Items">Tally sheet</a></li>
        <li>User</li>
        <li><a href="${g.base_url}/logout" title="Logout">Logout</a></li>
        <li><a href="${g.base_url}/login" title="Login">Login</a></li>
    </ul>
    </div>
    <div>
    <ul>

        <li><b>REPORTS</b></li>
        <li>Markup</li>
        <li><a href="${g.base_url}/markup/daily/" title="List of Daily Budget Release">Daily Expense</a></li>
        <li><a href="${g.base_url}/markup/weekly/" title="List of Weekly Budget Allotment">Weekly Budget Allotment</a></li>
        <li>CashFlow</li>
        <li><a href="${g.base_url}/budget/cashflow_daily" title="List of Daily Budget Release">Daily</a></li>
        <li><a href="${g.base_url}/budget/cashflow" title="List of Weekly Budget Allotment">Monthly</a></li>
        <li><a href="${g.base_url}/budget/cashflow_yearly" title="List of Daily Budget Release">Yearly</a></li>

    </ul>
    </div>

    <div>
    <ul>
        <li class="menuTop"><strong>Master</strong></li>
        <li><a href="${g.base_url}/area/" title="List of Areas">Areas</a></li>
        <li><a href="${g.base_url}/agent/" title="List of Agents">Agents</a></li>
        <li><a href="${g.base_url}/customer/" title="List of Customers">Customers</a></li>
        <li><a href="${g.base_url}/item/" title="List of Items">Item</a></li>
        <li><a href="${g.base_url}/uploads/item/" title="Upload CSV List of Items">Upload Items</a></li>
        <li><a href="${g.base_url}/cheques/" title="List of Cheques">Cheques</a></li>
    </ul>
    </div>

    <div>
    <ul>
        <li class="menuTop"><strong>Admin</strong></li>
        <li><a href="${g.base_url}/admin/user/" title="List of Users">Users</a></li>
    </ul>
    </div>

    <div>
    <ul>
        <li class="menuTop">Back End</li>
        <li><a href="${g.base_url}/transaction/" title="List of Transactions">Transactions</a></li>

    </ul>
    </div>
</div>

</div>

<div id="main">
## ${self.body()}
## ${next.body()}
${self.body()}
</div>

<div id="footer">
<p>Copyright &copy; Nebo</p>
</div>

</body>

</html>
