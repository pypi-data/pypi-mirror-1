<%doc>
list.mako - Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-03-17
    2008-03-18

</%doc>
<%inherit file="list_base.mako"/>

<div id="list-page">
<h1>${c.title}</h1>

<%
%>

<script language="javascript" type="text/javascript">
<!--

function show_details(id) {
        new Ajax.Updater('details' + id, 'list_details?id=' + id, {asynchronous:true, evalScripts:true});
}

//-->
</script>

${self.area_chooser()}
${self.show_table(c.table, c.columns, c.entries)}

</div>

