<%doc>
list_base.mako - Base List Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-18

</%doc>
<%inherit file="/list_base.mako"/>

<%
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
    if col in ('area', 'customer', 'agent'):
        value = '<a href="/delivery_receipt/filtered_list?%s=%s" target="%s">%s</a>' % (col, v_id, col, value)
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
elif col in ('name', ):
    value = '<a href="/delivery_receipt/filtered_list?%s=%s" target="%s">%s</a>' % (col, entry.id, col, value)
else:
    pass
# Make sure that None will be shown as an empty string
if value is None:
    value = ''
%>
${value}
</%def>

<%def name="area_chooser()">
    <%
    from divimon import model
    try:
        selected = int(request.params['area'])
    except KeyError:
        selected = None
    except ValueError:
        selected = None
    areas = model.Session.query(model.Area)
    options = h.options_for_select(['',])
    options += h.options_for_select_from_objects(areas, 'name', 'id', selected)
    %>
    <% c_count = len(c.columns) + 1 %>
    <form>
    ${h.select('area', options, onchange='submit()')}
    </form>
</%def>

<%def name="show_table(table, columns, entries)">
    <%
    try:
        area = request.params['area']
    except KeyError:
        area = None
    from math import ceil
    try:
        entry_count = len(entries)
    except TypeError:
        entry_count = entries.count()
    if entry_count == 0:
        content = '<p>No entries found.</p>'
        if 'add' in c.list_functions:
            content += '</p><a href="add?area=%s" title="Create New Entry">Create New Entry</a>.</p>' % (area)
        return content
    start = ((c.page-1) * c.max_entries) + 1
    end = c.page * c.max_entries
    if end > entry_count:
        end = entry_count
    c.end_page = int(ceil( entry_count / float(c.max_entries) ))
    if len(c.columns_shown) > 0:
        columns = c.columns_shown
    columns = list(columns)
    if len(c.columns_hidden) > 0:
        for col in c.columns_hidden:
            try:
                columns.remove(col)
            except ValueError:
                Pass
    c.columns_additional = 2
    %>

    Entry ${start} to ${end} of ${entry_count}

    <form action="multi">
    ${h.hidden_field('area', area)}
    <table class="list-table">

    ${self.show_table_head(columns)}

    <tbody>
    % for entry in entries[start-1:end]:
    <tr>
        ${self.show_table_entry(entry, columns)}
    </tr>
    % endfor
    </tbody>

    <tfoot>
    <% c_count = len(columns) + c.columns_additional %>
    <td colspan="${c_count}">
    ${self.show_table_functions()}
    </td>
    </tr>
    </tfoot>

    </table>
    ${self.show_table_page()}
    </form>
</%def>



