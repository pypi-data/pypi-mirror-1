<%doc>
</%doc>

<%inherit file="/edit_child_base.mako"/>

<input type="hidden" name="${c.child}-id" value="${c.entry.id}" />
% for col in c.columns:
    % if col != 'id':
    <td>
    <%
        input = self.show_field(col)
    %>
    ${input}
    </td>
    % endif
% endfor
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

