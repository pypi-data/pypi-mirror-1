<%doc>
edit.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17

</%doc>
<%inherit file="/edit_base.mako"/>

<h1>${c.title}</h1>

<form name="editForm" action="populate" method="">

% if c.id is not None:
    <input type="hidden" name="id" value="${c.id}" />
% endif

<dl>
% for col in ('start_day','start_month','end_day','end_month','year'):
    <dt>${col}</dt>
    <dd>
        <input id="${col}" name="${col}" value="" />
    </dd>
% endfor
</dl>
<input type="submit" value="Populate" />

</form>


