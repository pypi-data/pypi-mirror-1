<%doc>
edit.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/transaction/edit_base.mako"/>

<h1>${c.title}</h1>

<form name="editForm" action="save" method="">

${self.show_children(c.entry)}

% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
<dl>

<% col='branch' %>
<dt>${col}</dt>
<dd>
${self.show_div_field(col)}
</dd>

<% col='type' %>
<dt>${col}</dt>
<dd>
${self.show_div_field(col)}
</dd>

<% col='total_price' %>
<dt>${col}</dt>
<dd>
${self.show_div_field(col)}
</dd>

<% col='total_tendered' %>
<dt>${col}</dt>
<dd>
${self.show_div_field_tendered(col)}
</dd>

<% col='change' %>
<dt>${col}</dt>
<dd>
${self.show_div_field(col)}
</dd>

</dl>

${self.show_properties()}

<input type="submit" value="Save" />

</form>


