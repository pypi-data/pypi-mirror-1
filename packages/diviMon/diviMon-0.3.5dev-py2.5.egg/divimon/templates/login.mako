<%doc>
blank.mako - Blank Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-04-03

</%doc>
<%inherit file="base.mako"/>

<%
%>

<h1>Login</h1>

% if c.msg:
    <span>
    ${c.msg}
    </span>
% endif
<form method="post">
<dl>
<dt>Username:</dt>
<dd><input id="user" name="user" /></dd>
<dt>Password:</dt>
<dd><input id="password" name="password" type="password" /></dd>
</dl>
<input type="submit" name="action" value="Login" />
</form>
