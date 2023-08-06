<%doc>
edit.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/edit_base.mako"/>

<%
%>

<%def name="show_children(entry)">
    %for child in c.children:
    <script language="javascript" type="text/javascript">
    <!--
    var column;
    var ${child}_cnt=0;
    var ${child}_price=Array();
    var old_${child}_cnt=0;

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

    function show_change() {
        total_price = parseFloat(document.getElementById('total_price').value);
        total_tendered = parseFloat(document.getElementById('total_tendered').value);
        change = document.getElementById('change');
        //new Ajax.Updater('div-change', 'show_change?price=' + price +'&amp;tendered=' + tendered, {asynchronous:true, evalScripts:true});
        change.value = total_tendered - total_price;
    }

    function show_total() {
        total = 0;
        for (cnt=1; cnt<=trans_item_cnt; cnt++) {
            total = total + parseFloat(document.getElementById('price-'+cnt).value);
        }
        document.getElementById('total_price').value = total;
    }

    function show_price(cnt) {
        price = document.getElementById('price-'+cnt);
        item = document.getElementById('item-'+cnt);
        qty = document.getElementById('qty-'+cnt);
        new Ajax.Updater('div-price-'+cnt, 'show_price?cnt='+cnt+'&amp;item='+item.value+'&amp;qty='+qty.value, {asynchronous:false, evalScripts:true});
        //new Ajax.Updater('div-total_price', 'show_total_price', {asynchronous:true, evalScripts:true});
        //new Ajax.Updater('div-change', 'show_change?price='+total_price.value +'&amp;tendered='+total_tendered.value, {asynchronous:true, evalScripts:true});
        show_total();
        show_change();
    }

    function change_total() {
        //alert(old_trans_item_cnt);
        total = 0;
        for (cnt=1; cnt<=old_trans_item_cnt; cnt++) {
            total = total + parseFloat(document.getElementById('old-price-' + cnt).value);
        }
        document.getElementById('total_price').value = total;
    }

    function change_price(cnt) {
        unit_price = parseFloat(document.getElementById('old-item-' + cnt).value);
        qty = parseFloat(document.getElementById('old-received_qty-' + cnt).value);
        t_price = unit_price * qty;
        //alert(t_price);
        document.getElementById('old-price-'+cnt).value = t_price;
        change_total();
    }

    //-->
    </script>
        ${self.show_child(child, entry)}
    %endfor
</%def>

<%def name="show_child(child, entry)">
    <div id="${child}-children" class="children">
    <%
    parent_entry = entry
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
    <input type="hidden" name="${child}.id" value="${entry.id}" />
    <tr id="old-${child}-${child_cnt}">
    %   for column in child_details['columns']:
        <td>
        ${self.show_child_value(child, entry, column, child_cnt)}
        </td>
    %   endfor
    <td>
    <!--<a href="#${child}" onclick="edit_child_${child}(${child_cnt}, ${entry.id}, ${c.entry.id});">edit</a>-->
    ${h.link_to_remote('remove',
            dict(update='old-'+child+'-'+str(child_cnt), url=h.url_for(
                action='rem_child',
                id=entry.id,
                child=child,
                p_id=parent_entry.id,
            ))
        )}
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
    <script language="javascript" type="text/javascript">
    <!--
    old_${child}_cnt++;
    //-->
    </script>
</%def>

<%def name="show_child_value(child, entry, col, cnt)">
    <%
    child_details = c.children[child]
    parent = child_details['parent']
    table = entry.__class__
    tbl_col = getattr(table.c, col)
    value = getattr(entry, col)
    parent_entry = None
    if value is None:
        ''
    elif len(tbl_col.foreign_keys) > 0:
        v_id = value
        table = parent[col]['table']
        parent_entry = c.db_sess.query(table).get(v_id)
        try:
            value = getattr(parent_entry, parent[col]['column'])
        except AttributeError:
            value = ''
    else:
        pass
    if value is None:
        ''
    %>
    % if col == 'received_qty':
        <input id="old-${col}-${cnt}" name="${child}.${col}" value="${getattr(entry, 'qty')}"
            onkeyup="change_price(${cnt});"
            />
    % elif col == 'item':
        <input id="old-${col}-${cnt}" value="${parent_entry.price}" type="hidden" />
        ${value}
    % elif col == 'price':
        <input id="old-${col}-${cnt}" name="${child}.${col}" value="${value}" 
            onkeyup="change_total();"
            />
    % else:
        <input id="old-${col}-${cnt}" name="${child}.${col}" value="${value}" readonly="readonly" />
    % endif
</%def>

<%def name="show_value(col)">
    <%
    from divimon import model
    tbl_col = getattr(c.table.c, col)
    value = getattr(c.entry, col)
    if value is None:
        value = ''
    if len(tbl_col.foreign_keys) > 0:
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
        entry = model.get(parent['table'], value)
        value = getattr(entry, p_column)
    if value is None:
        value = ''
    %>
    ${value}
</%def>

<%def name="show_div_field(col)">
    <%
    if col == 'total_tendered':
        return show_div_field_tendered(col)
    %>
    <div id="div-${col}">
    ${self.show_field(col)}
    </div>
</%def>

<%def name="show_div_field_tendered(col)">
    <div id="div-${col}">
    <input id="${col}" name="${col}"
        onkeyup="show_change();"
        onkeydown="show_change();"
        />
    </div>
</%def>

<%def name="show_field_select(col)">
    <%
    v_id = getattr(c.entry, col)
    area_id = request.params['area']
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
    try:
        p_entries = c.db_sess.query(p_table).filter_by(area=area_id)
    except:
        pass
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

