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
% for col in c.columns:
    % if col == 'password':
    <dt>Password</dt>
    <dd>
    <input type="password" name="password" />
    </dd>
    <dt>Confirm Password</dt>
    <dd>
    <input type="password" name="password2" />
    </dd>
    % elif col != 'id':
    <dt>${col}</dt>
    <dd>
    <%
        input = self.show_field(col)
    %>
    ${input}
    </dd>
    % endif
% endfor

</dl>

<input type="submit" value="Save" />


</form>


