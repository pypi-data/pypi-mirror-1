<%doc>
</%doc>

<%
child = c.child
parent = c.child_details['parent']
child_cnt = 0
try:
    child_label = c.child_details['label']
except KeyError:
    child_label = child
%>


<%def name="get_value(entry, col)">
    <%
    parent = c.child_details['parent']
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

<h3>${child_label}</h3>
<table>
<thead>
<tr>
%for column in c.child_details['columns']:
    <th>
    ${column}
    </th>
%endfor
</tr>
</thead>
<tbody>
%for entry in c.children:
<%
child_cnt += 1
%>
<tr id="old-${child}-${child_cnt}">
%   for column in c.child_details['columns']:
    <td>
    ${self.get_value(entry, column)}
    </td>
%   endfor
<td>
<a href="#${child}" onclick="edit_child_${child}(${child_cnt}, ${entry.id}, ${c.parent.id});">edit</a>
</td>
</tr>
%endfor
%for cnt in range(1, 1+50):
    <tr id="new-${child}-${cnt}"></tr>
%endfor
</tbody>
</table>
<a href="#${child}" onclick="add_child_${child}();">add</a>
<a name="${child}">&nbsp;</a>

