<%doc>
</%doc>

<%inherit file="/edit_child_base.mako"/>

<%
%>

<input type="hidden" name="${c.child}-id" value="${c.entry.id}" />

<% col = 'item' %>
<td>
<%
    from divimon import model
    v_id = getattr(c.entry, col)
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
    print parent['table']
    entry = model.get(parent['table'], v_id)
    value = getattr(entry, p_column)
%>
${value}
${h.hidden_field('trans_item.item', v_id)}
</td>

<%
col = 'qty'
value = getattr(c.entry, col)
%>
<td>
    ${value}
    ${h.hidden_field('trans_item.qty', value)}
</td>

<%
col = 'price'
value = getattr(c.entry, col)
%>
<td>
    ${value}
    ${h.hidden_field('trans_item.price', value)}
</td>

<% col = 'received_qty' %>
<td>
<%
    input = self.show_field(col)
%>
${input}
</td>

<td class="child-remove-link">
${h.link_to_remote('remove',
        dict(update='old-'+c.child+'-'+c.cnt, url=h.url_for(
            action='rem_child',
            id=c.entry.id,
            child=c.child,
            p_id=c.p_id,
        ))
    )}
</td>

