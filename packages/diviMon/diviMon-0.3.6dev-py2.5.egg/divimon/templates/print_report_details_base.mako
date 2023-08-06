<%doc>
details_base.mako - Base List Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-18

</%doc>
<%inherit file="print_base.mako"/>

<%
from datetime import datetime
now = datetime.now()
%>

<%def name="get_value(entry, col)">
<%
from sqlalchemy import types
from divimon import model
table = entry.__class__
tbl_col = getattr(table.c, col)
value = getattr(entry, col)
if value is None:
    value = ''
elif len(tbl_col.foreign_keys) > 0:
    v_id = value
    table = c.parent[col]['table']
    entry = c.db_sess.query(table).get(v_id)
    try:
        value = getattr(entry, c.parent[col]['column'])
    except AttributeError:
        value = ''
elif isinstance(tbl_col.type, types.DateTime):
    from datetime import datetime
    now = datetime.now()
    v = getattr(entry, col)
    '''
    if v <= now:
        value = '%s ago' % h.date.time_ago_in_words(v)
    else:
        value = '%s from now' % h.date.time_ago_in_words(v)
    '''
    date_diff = now.date() - v.date()
    date_diff = date_diff.days
#    if date_diff == 0:
#        value = v.strftime('%H:%M')
#    elif date_diff == 1:
#        value = 'Yesterday ' + v.strftime('%H:%M')
#    elif date_diff < 7:
#        value = v.strftime('%a %H:%M')
#    elif now.year == v.year:
#        value = v.strftime('%b %d')
#    else:
#        value = v.strftime('%Y %b %d')
    value = v.strftime('%Y %b %d')
    value = '<span style="text-transform: capitalize;">%s</span>' % value
elif col in ('sender', 'recipient'):
    for contact in c.contacts:
        for phone in contact.phone:
            if value.endswith(phone.number):
                value = '<a title="%s">%s</a>' % (value, contact.name)
else:
    pass
# Make sure that None will be shown as an empty string
if value is None:
    value = ''
%>
${value}
</%def>

<%def name="show_children(entry)">
    %for child in c.children:
    <script language="javascript" type="text/javascript">
    <!--
    var column;
    var ${child}_cnt=0;

    function add_child_${child}(child) {
        ${child}_cnt++;
        new Ajax.Updater('new-${child}-'+${child}_cnt, 'add_child?child=${child}&amp;cnt='+${child}_cnt, {asynchronous:true, evalScripts:true});
        //document.${child}-cnt.display: block;
        //return false;
    }

    function edit_child_${child}(cnt, id, p_id) {
        //${child}_cnt++;
        new Ajax.Updater('old-${child}-'+cnt, 'edit_child?c_id='+id+'&amp;p_id='+p_id+'&amp;child=${child}&amp;cnt='+cnt, {asynchronous:true, evalScripts:true});
        //document.${child}-cnt.display: block;
        //return false;
    }

    //-->
    </script>
        ${self.show_child(child, entry)}
    %endfor
</%def>

<%def name="show_child(child, entry)">
    <%
    child_details = c.children[child]
    child_cols = child_details['columns']
    child_entries = getattr(c.entry, child)
    try:
        child_label = child_details['label']
    except KeyError:
        child_label = child
    %>
    <div class="children">
    <h3>${child_label}</h3>
    <table>
    <thead>
    <tr>
    %for col in child_cols:
        <th>${col}</th>
    %endfor
    </tr>
    </thead>
    <tbody>
    %for child_entry in child_entries:
        <tr>
        %for col in child_details['columns']:
            <td>
            ${show_child_value(child, child_entry, col)}
            </td>
        %endfor
        <tr>
    %endfor
    </tbody>
    </table>
    </div>
</%def>

<%def name="show_child_value(child, entry, col)">
    <%
    child_details = c.children[child]
    parent = child_details['parent']
    table = entry.__class__
    tbl_col = getattr(table.c, col)
    value = getattr(entry, col)
    if value is None:
        ''
    elif len(tbl_col.foreign_keys) > 0:
        v_id = value
        table = parent[col]['table']
        entry = c.db_sess.query(table).get(v_id)
        try:
            value = getattr(entry, parent[col]['column'])
        except AttributeError:
            value = ''
    else:
        pass
    if value is None:
        ''
    %>
    ${value}
</%def>

