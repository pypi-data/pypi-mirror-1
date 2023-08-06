<%doc>
/sale/edit.mako - Custom Sale Edit Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/transaction/edit_base.mako"/>

<%
    from divimon import model
    area_id = request.params['area']
    area_name = model.get(model.Area, area_id).name
%>

<h1>${c.title} <small>(${area_name})</small></h1>

<form name="editForm" action="save" method="">
% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif
${h.hidden_field('area', area_id)}

<dl>
% for col in c.columns:
    % if col not in ('id', 'created', 'type', 'area'):
        <%
        if col == 'branch' and g.branch_id > 0:
            continue
        endif
        %>
    <dt>${col}</dt>
    <dd>
    <%
        input = self.show_div_field(col)
    %>
    ${input}
    </dd>
    % endif
% endfor

${self.show_properties()}

${self.show_children(c.entry)}

</dl>

<input type="submit" value="Save" />

</form>


