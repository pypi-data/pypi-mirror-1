<%doc>
list_base.mako - Base List Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-18

</%doc>
<%inherit file="details_base.mako"/>

<%
%>

<%def name="show_table_head(columns)">
    <thead>
    <tr>
    <% c_count = len(columns) + c.columns_additional %>
    <td colspan="${c_count}">
    ${self.show_table_functions()}
    </td>
    </tr>
    <tr>
    <th width="12px">
        <input name="select_all"
            onchange="return check_all(this.checked, this.form.select);"
            type="checkbox" />
    </th>
    <th>
    </th>
    %for col in columns:
    <th>
        %if col in c.column_descriptions.keys():
            ${c.column_descriptions[col]}
        %else:
            ${col}
        %endif
    </th>
    %endfor
    </tr>
    </thead>
</%def>

<%def name="show_table_entry_functions(entry)">
    <% function='details' %>
    %if function in c.entry_functions:
    <a href="${function}?id=${entry.id}" title="${function}"
        ><img src="${g.base_url}/icons/${function}.png" alt="${function}" class="function-image" /></a>
    %endif
    <% function='edit' %>
    %if function in c.entry_functions:
    <a href="${function}?id=${entry.id}" title="${function}"
        ><img src="${g.base_url}/icons/${function}.png" alt="${function}" class="function-image" /></a>
    %endif
    <% function='delete' %>
    %if function in c.entry_functions:
    <a onclick="return areyousure('You sure you want to delete this entry?')"
        href="${function}?id=${entry.id}" title="${function}"
        ><img src="${g.base_url}/icons/${function}.png" alt="${function}" class="function-image" /></a>
    %endif
</%def>


<%def name="show_table_entry(entry, columns)">
    <td>
        <input name="select" value="${entry.id}" id="select-${entry.id}"
            type="checkbox" />
    </td>
    <th class="crud">${self.show_table_entry_functions(entry)}</th>
    % for col in columns:
    <td>
        ${self.get_value(entry, col)}
    </td>
    % endfor
</%def>

<%def name="show_table_pagination()">
    <span class="pagination">
    %if c.page > 1:
        <% self.kwargs['page'] = 1 %>
        <a href="?${h.cgi_for(**self.kwargs)}" title="Go to First Page"
            ><img src="${g.base_url}/icons/first.png" alt="&lt;&lt; First" /></a>
        <% self.kwargs['page'] = c.page-1 %>
        <a href="?${h.cgi_for(**self.kwargs)}" title="Go to Page ${c.page-1}"
            ><img src="${g.base_url}/icons/prev.png" alt="&lt; Prev" /></a>
    %endif
        <a href="#" onclick="window.reload()"
            >Page ${c.page}</a> of ${c.end_page}
    %if c.page < c.end_page:
        <% self.kwargs['page'] = c.page+1 %>
        <a href="?${h.cgi_for(**self.kwargs)}" title="Go to Page ${c.page+1}"
            ><img src="${g.base_url}/icons/next.png" alt="Next &gt;" /></a>
        <% self.kwargs['page'] = c.end_page %>
        <a href="?${h.cgi_for(**self.kwargs)}" title="Go to Last Page"
            ><img src="${g.base_url}/icons/last.png" alt="Last &gt;&gt;" /></a>
    %endif
    </span>
</%def>


<%def name="show_table_functions()">
    %if 'delete' in c.list_functions:
    <span class="function">
        <input onclick="return areyousure('You sure you want to delete these entries?')"
            name="function" type="submit" value="${g.function_delete}" />
    </span>
    %endif
    %if 'add' in c.list_functions:
    <span class="function">
        <input onclick="this.form.action='add';"
            name="function" type="submit" value="New" />
    </span>
    %endif
    ${self.show_table_pagination()}
</%def>


<%def name="show_table_page()">
    <%
    from math import ceil
    if c.end_page == 1:
        return ''
    elif c.end_page <= g.show_pages:
        start = 1
        end = c.end_page
    elif c.page >= c.end_page - (g.show_pages/2):
        end = c.end_page
        start = end - g.show_pages + 1
    elif c.page > g.show_pages/2:
        start = c.page - (g.show_pages/2) + 1
        end = start + g.show_pages - 1
    else:
        start = 1
        end = start + g.show_pages - 1
    %>
    <span class="page-list">
    <input type="hidden" name="page" value="${c.page}" />
    %if end > 1:
        Pages:
    %endif
    %if start > 1:
        <% self.kwargs['page'] = max(c.page-g.show_pages, 1) %>
        <a href="?${h.cgi_for(**self.kwargs)}"
            title="Show Previous Set of Pages"
            >...</a>
    %endif
    %for a in range(start, end+1):
        <%
        if a == c.page:
            #a = '<strong>%s</strong>' % a
            pass
        self.kwargs['page'] = a
        %>    
        %if a == c.page:
            <a href="?${h.cgi_for(**self.kwargs)}" title="Go to page ${a}"><strong>${a}</strong></a>
        %else:
            <a href="?${h.cgi_for(**self.kwargs)}" title="Go to page ${a}">${a}</a>
        %endif
    %endfor
    %if end < c.end_page:
        <% self.kwargs['page'] = min(c.page+g.show_pages, c.end_page) %>
        <a href="?${h.cgi_for(**self.kwargs)}"
            title="Show Next Set of Pages"
            >...</a>
    %endif
    </span>
</%def>


<%def name="show_table(table, columns, entries)">
    <%
    from math import ceil
    try:
        entry_count = len(entries)
    except TypeError:
        entry_count = entries.count()
    if entry_count == 0:
        content = '<p>No entries found.</p>'
        if 'add' in c.list_functions:
            content += '</p><a href="add" title="Create New Entry">Create New Entry</a>.</p>'
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

