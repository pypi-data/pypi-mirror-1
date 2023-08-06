<%doc>
blank.mako - Blank Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-04-03

</%doc>
<%inherit file="base.mako"/>

<%
%>

<%def name="show_table(table, cols, rows)">
<table class="list-table">
    <thead>
    <tr>
    % for col in cols:
        <th>
        <%
        options = h.options_for_select(cols, col)
        %>
        ${h.select('column', options)}
        </th>
    % endfor
    </tr>
    </thead>

    <tbody>
    % for row in rows[0:5]:
    <tr>
        <%
        col_cnt = 0
        %>
        % for col in cols:
            <%
            try:
                value = row[col_cnt]
            except IndexError:
                value = ''
            col_cnt += 1
            %>
            <td>
            ${value}
            </td>
        % endfor
    </tr>
    % endfor
    </tbody>
<table>
</%def>

<div id="list-page">
<h1>Upload ${c.title}</h1>

<form action="save" target="_blank">
${self.show_table(c.table, c.columns, c.rows)}
${h.submit("Save")}
</form>

</div>



