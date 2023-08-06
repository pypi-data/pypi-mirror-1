<%doc>
blank.mako - Blank Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-04-03

</%doc>
<%inherit file="base.mako"/>

<%
%>

<h1>Upload ${c.title}</h1>

<form action="upload" enctype="multipart/form-data" method="post">
<dl>
<dt>Required Columns</dt>
<dd>${', '.join(c.columns)}</dd>
<dt>Upload file</dt>
<dd>${h.file_field('file')}</dd>
</dl>
${h.submit('Submit')}
${h.end_form()}

