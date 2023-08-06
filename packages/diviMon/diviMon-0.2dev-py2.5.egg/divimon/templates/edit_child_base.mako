<%doc>
</%doc>

<%def name="show_field(col)">
    <%
    from sqlalchemy import types
    value = getattr(c.entry, col)
    if value is None:
        value = ''
    tbl_col = getattr(c.table.c, col)
    %>
    % if len(tbl_col.foreign_keys) > 0:
        ${self.show_field_select(col)}
    % elif isinstance(tbl_col.type, types.Boolean):
        <input type="checkbox"
            %if tbl_col.default.arg:
                checked="checked"
            %endif
            name="${c.child}.${col}" />
    % elif isinstance(tbl_col.type, (types.Text, types.UnicodeText)):
        <textarea name="${c.child}.${col}" cols="32" rows="6">${value}</textarea>
    % elif isinstance(tbl_col.type, types.Date):
        <input name="${c.child}.${col}" value="${value}" /><small>(YYYY-MM-DD)</small>
    % elif isinstance(tbl_col.type, types.DateTime):
        <input name="${c.child}.${col}" value="${value}" /><small>(YYYY-MM-DD HH:MM)</small>
    % elif isinstance(tbl_col.type, types.Time):
        <input name="${c.child}.${col}" value="${value}" /><small>(HH:MM)</small>
    % else:
        <input name="${c.child}.${col}" value="${value}" />
    % endif
</%def>

<%def name="show_field_select(col)">
    <%
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
    p_entries = c.db_sess.query(p_table)
    %>
    <select name="${c.child}.${col}">
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

${self.body()}

