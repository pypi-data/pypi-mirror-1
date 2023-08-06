<%doc>
list_base.mako - Base List Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-18

</%doc>
<%inherit file="/list_base.mako"/>

<%
%>

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



