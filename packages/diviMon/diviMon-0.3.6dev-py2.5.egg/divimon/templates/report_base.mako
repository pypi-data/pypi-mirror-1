<%doc>
base.mako - Base template for the SMSShell application

Modify this template if you want to change the overall look of the application.

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title> ${c.title} POS </title>
<link href="${g.base_url}/smsshell.css" type="text/css" rel="stylesheet" />
<link href="${g.base_url}/hh.css" type="text/css" rel="stylesheet" />
<script src="${g.base_url}/js/areyousure.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/list.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/show_hide.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/text_counter.js" language="javascript" type="text/javascript"></script>
<script src="${g.base_url}/js/server.js" language="javascript" type="text/javascript"></script>
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
        <li>Reports</li>
        <li><a href="${g.base_url}/expense/" title="List of Daily Budget Release">Budget - Daily Release</a></li>
        <li><a href="${g.base_url}/budget/" title="List of Weekly Budget Allotment">Budget - Weekly Allotment</a></li>
        <li>Stocks</li>
        <li><a href="${g.base_url}/inventory/" title="Inventory">Inventory</a></li>
        <li><a href="${g.base_url}/stocks_out/" title="Stocks Out">Stocks Out</a></li>

    </ul>
    </div>

    <div>
    <ul>
        <li class="menuTop">Master</li>
        <li><a href="${g.base_url}/area/" title="List of Areas">Areas</a></li>
<!--         <li><a href="${g.base_url}/classification/" title="List of Classifications">Classifications</a></li> -->
        <li><a href="${g.base_url}/agent/" title="List of Agents">Agents</a></li>
        <li><a href="${g.base_url}/customer/" title="List of Customers">Customers</a></li>
        <li><a href="${g.base_url}/item/" title="List of Items">Item</a></li>
        <li><a href="${g.base_url}/cheques/" title="List of Cheques">Cheques</a></li>
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
