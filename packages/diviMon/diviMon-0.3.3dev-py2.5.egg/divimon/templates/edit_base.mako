<%doc>
edit_base.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<% import re %>

<%inherit file="/base.mako"/>

<%def name="get_type(col)">
    <%
    col_type = getattr(c.table.c, col).type
    if col_type:
        type = 'test'
    %>
</%def>

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
            id="${col}" name="${col}" />
    % elif isinstance(tbl_col.type, (types.Text, types.UnicodeText)):
        <textarea id="${col}" name="${col}" cols="32" rows="6"
            >${value}</textarea>
    % elif isinstance(tbl_col.type, types.Date):
        <input id="${col}" name="${col}" value="${value}" /><small>(YYYY-MM-DD)</small>
    % elif isinstance(tbl_col.type, types.DateTime):
        <input id="${col}" name="${col}" value="${value}" /><small>(YYYY-MM-DD HH:MM)</small>
    % elif isinstance(tbl_col.type, types.Time):
        <input id="${col}" name="${col}" value="${value}" /><small>(HH:MM)</small>
    % else:
        <input id="${col}" name="${col}" value="${value}" />
    % endif
</%def>

<%def name="show_field_select(col)">
    <%
    v_id = getattr(c.entry, col)
    try:
        parent = c.parent[col]
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
    <select id="${col}" name="${col}">
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

<%def name="show_properties()">
    %for prop in c.properties:
    <%
    from divimon import model
    parent_field = prop[0]
    prop_field = prop[1]
    prop_table = prop[2]
    properties = getattr(c.entry, parent_field)
    prop_entries = model.list(prop_table)
    %>
    <dt>${parent_field}</dt>
    <dd>
        <select name="${parent_field}" multiple="multiple">
        %for prop in prop_entries:
            <option value="${prop.id}"
                %if prop in properties:
                    selected="selected"
                %endif
                >${getattr(prop, prop_field)}</option>
        %endfor
        </select>
    </dd>
    %endfor
</%def>

<%def name="show_child(child, entry)">
    <div id="${child}-children" class="children">
    <%
    child_details = c.children[child]
    try:
        child_label = child_details['label']
    except KeyError:
        child_label = child
    child_entries = getattr(entry, child)
    parent = child_details['parent']
    child_cnt = 0
    try:
        child_label = child_details['label']
    except KeyError:
        child_label = child
    %>
    <h3>${child_label}</h3>
    <table>
    <thead>
    <tr>
    %for column in child_details['columns']:
        <th>
        ${column}
        </th>
    %endfor
    </tr>
    </thead>
    <tbody>
    %for entry in child_entries:
    <%
    child_cnt += 1
    %>
    <tr id="old-${child}-${child_cnt}">
    %   for column in child_details['columns']:
        <td>
        ${self.show_child_value(child, entry, column)}
        </td>
    %   endfor
    <td>
    <a href="#${child}" onclick="edit_child_${child}(${child_cnt}, ${entry.id}, ${c.entry.id});">edit</a>
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
    </div>
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

    function show_price(cnt) {
        price = document.getElementById('price-'+cnt);
        item = document.getElementById('item-'+cnt);
        qty = document.getElementById('qty-'+cnt);
        total_price = document.getElementById('total_price');
        new Ajax.Updater('div-price-'+cnt, 'show_price?cnt='+cnt+'&amp;item='+item.value+'&amp;qty='+qty.value, {asynchronous:true, evalScripts:true});
    }

    //-->
    </script>
        ${self.show_child(child, entry)}
    %endfor
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

