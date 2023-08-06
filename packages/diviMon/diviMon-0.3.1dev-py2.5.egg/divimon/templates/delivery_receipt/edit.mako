<%doc>
/sale/edit.mako - Custom Sale Edit Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/transaction/edit_base.mako"/>

<h1>${c.title}</h1>

<form name="editForm" action="save" method="">
% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif

<dl>

<% col = 'total_price' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_div_field(col)
%>
${input}
</dd>

<% col = 'area' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_value(col)
%>
${input}
</dd>

<% col = 'customer' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_value(col)
%>
${input}
</dd>

<% col = 'agent' %>
<dt>${col}</dt>
<dd>
<%
    input = self.show_value(col)
%>
${input}
</dd>

${self.show_properties()}

${self.show_children(c.entry)}

</dl>

<input type="submit" value="Save" />

</form>


