<%doc>
edit.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/edit_base.mako"/>

<%
%>

<h1>User</h1>

<form name="editForm" action="submit" method="">
% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
<dl>

<% col = 'name' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

<% col = 'password' %>
<dt>${col}</dt>
<dd>
<input type="password" name="password" />
</dd>
<dt>Confirm ${col}</dt>
<dd>
<input type="password" name="password2" />
</dd>

<% col = 'role' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

<% col = 'email_address' %>
<dt>Email Address</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

<% col = 'details' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_field(col)
%>
${input}
</dd>

</dl>

<input type="submit" value="Submit" />

</form>


