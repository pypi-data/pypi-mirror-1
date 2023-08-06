<%doc>
details.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="print_details_base.mako"/>
<%inherit file="print_list_base.mako"/>

<h1>HH Marketing</h1>
<h2>Sales Order</h2>

<!--dl>
% for col in c.columns:
    <%print col%>
    % if col != 'id':
    <dt>${col}</dt>
    <dd>${self.get_value(c.entry, col)}</dd>
    % endif
% endfor
</dl-->

<dl>
    <dd>Sales Order No.: ${self.get_value(c.entry, 'id')}</dd>
    <dt>Customer Name: ${self.get_value(c.entry, 'customer')}</dt>
    <dd>Date: ${self.get_value(c.entry, 'created')}</dd>
    <dt>Address: ${self.get_value(c.entry, 'area')}</dt>
    <dd>Terms: ${self.get_value(c.entry, 'pay_type')}</dd>
</dl>



% if len(c.children) > 0:
##Show Children
% for column, child_details in c.children.iteritems():
    <%
    child_tbl = child_details['table']
    child_cols = child_details['columns']
    children = getattr(c.entry, column)
    c.list_functions = []
    c.entry_functions = []
    %>
    ${self.show_children(c.entry)}
% endfor
% endif
<dl>
    <dd>Total Amount ${self.get_value(c.entry, 'total_price')}</dd>
</dl>
