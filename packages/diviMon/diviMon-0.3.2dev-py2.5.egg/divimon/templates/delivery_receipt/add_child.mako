<%doc>
</%doc>

<%inherit file="/add_child_base.mako"/>


<%def name="show_field_item(col)">
    <%
    try:
        v_id = getattr(c.entry, col)
    except AttributeError:
        v_id = ''
    try:
        parent = c.child_details['parent'][col]
    except KeyError:
        raise KeyError('The column %s should be defined as a parent.' % (col))
    try:
        p_table = parent['table']
    except KeyError:
        raise KeyError('The table for the parent %s should be specified.' % (col))
    try:
        p_column = parent['column']
    except KeyError:
        raise KeyError('The column for the parent %s should be specified.' % (col))
    p_entries = c.db_sess.query(p_table)
    %>
    <select id="${col}-${c.cnt}" name="${c.child}.${col}"
        onchange="show_price('${c.cnt}')"
        >
    %if getattr(c.table.c, col).nullable:
        <option value=""></option>
    %endif
    %for entry in p_entries:
        %if entry.id == v_id:
            <option value="${entry.id}" selected="selected">
                ${getattr(entry, p_column)}
            </option>
        %else:
            <option value="${entry.id}">
                ${getattr(entry, p_column)}
            </option>
        %endif
    %endfor
    </select>
</%def>


<%
col = 'item'
%>
<td>
    ${self.show_field_item(col)}
</td>

<%
col = 'qty'
%>
<td>
    <input id="${col}-${c.cnt}" name="${c.child}.${col}"
        value="1"
        onchange="show_price('${c.cnt}')"
        onkeyup="show_price('${c.cnt}')"
        onkeydown="show_price('${c.cnt}')"
        />
</td>

<%
col = 'price'
%>
<td>
    <div id="div-${col}-${c.cnt}">
    <input id="${col}-${c.cnt}" name="${c.child}.${col}"
        />
    </div>
</td>

<td class="child-remove-link">
${h.link_to_remote("remove",
        dict(update='new-'+c.child+'-'+c.cnt, url=h.url_for(action='blank_out'))
    )}
</td>
Hello

