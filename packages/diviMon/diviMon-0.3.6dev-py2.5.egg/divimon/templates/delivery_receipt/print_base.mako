<%doc>
print_base.mako - Base template drived from base.mako for the SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17
    2008-07-28

</%doc>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"
   "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
<title> ${c.title} POS </title>
<link href="${g.base_url}/dr_print.css" type="text/css" rel="stylesheet" />
${h.javascript_include_tag(builtins=True)}
</head>

<body>



<div id="main">
${self.body()}
</div>

<div id="footer">
</div>

</body>

</html>
