<%doc>
blank.mako - Blank Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-04-03

</%doc>
<%inherit file="base.mako"/>

<h1>Upload ${c.title}</h1>

${h.form(h.url(action='upload'), multipart=True)}
Upload file:      ${h.file_field('file')} <br />
                  ${h.submit('Submit')}
${h.end_form()}

