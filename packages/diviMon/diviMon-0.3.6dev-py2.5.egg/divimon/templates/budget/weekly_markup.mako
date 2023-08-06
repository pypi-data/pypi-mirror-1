<%doc>
daily_markup.mako - Template for DiviMon application

AUTHOR: Erwin Pacheco <erwin.pacheco@gmail.com>

Modification Dates:
    2008-07-23

</%doc>
<%inherit file="/report_list_base.mako"/>

<% c_count = len(c.columns) + 1 %>

<div id="list-page">
<h1>${c.title} Report</h1>

<%
from datetime import datetime,timedelta
now = datetime.now()
today = datetime(now.year, now.month, now.day, 0, 0)
tomorrow = today + timedelta(1)
cur_month = datetime.now().month
beg_day = datetime(now.year, now.month, 1, 0, 0)
end_day = datetime(now.year, now.month, 31, 23, 59)
months = ['','January','February','March','April','May','June','July','August','September','October','November','December']
days = range(1,31)
sample_date = datetime(now.year, now.month, days[0], 0, 0)
day1 = datetime.weekday(sample_date)
weeks = list()
week = list()
total_markup = 0
week_total_markup = 0
week_end = 0
print '----------------------'
print(now)

print 'day1: ' + str(day1)
if day1 > 0:                                        #day1 is not monday
    for day in range(0,day1-1):
        week.append(0)
    endfor

    for rday in range(day1-1,7):
        week.append(rday-day1+1)
    endfor

    weeks.append(week)

    try:
        week_end = week[6]
    except IndexError:
        pass
    week = list()
    cnt = 0
    for day in range(week_end+1,31):
        if cnt>6:
            cnt=0
            weeks.append(week)
            week = list()
        cnt += 1
        week.append(day)
    weeks.append(week)
else:
    cnt = 0
    for day in days:
        week.append(day)
        if cnt >6:
            cnt=0
            weeks.append(week)
            week = list()
        cnt += 1
    if week != list():
        weeks.append(week)
        week = list()
print weeks
%>
Weeks during the month of ${months[now.month]} ${now.year}<br>

<%
week_cnt = 0
%>
%for week in weeks:
    <%
    cnt = 0
    week_cnt += 1

    weekday1 = week[0]
    try:
        weekday6 = week[6]
    except  IndexError:
        weekday6 = 'last day'
    if weekday1 < 1:
        weekday1 = 1
    if weekday6 < 1:
        weekday6 = 30
    %>
    <br><br>Week ${week_cnt} from ${months[now.month]} ${weekday1} to ${weekday6}
<table>

    %for day in week:
        %if day>0:
        <%
            beg_day = datetime(now.year, now.month, day, 0, 0)
            end_day = datetime(now.year, now.month, day, 23, 59)
            from divimon import model
            Sales = model.Session.query(model.Transaction).filter(model.Transaction.created<=end_day).filter(model.Transaction.created>=beg_day)
            markup = 0
        %>


            %for sale in Sales:
<tr>
<ul>
    <td>
        <tr>
        <td>DR  #${sale.id} &nbsp ${sale.created.month}/${sale.created.day}/${sale.created.year} </td>
        <td>&nbsp - &nbsp</td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td>P</td>
                <%
                from divimon import model
                TransItems = model.Session.query(model.TransItem).filter_by(transaction=sale.id)
                beg_sale = 0
                total_orig_price = 0
                %>
                %for titem in TransItems:
                    <%
                    from divimon import model
                    Item = model.Session.query(model.Item).filter_by(id=titem.item)
                    total_orig_price += int(Item[0].purchase_price) * int(titem.qty)
                    %>
                %endfor
                    <%
                    markup = int(sale.total_price) - int(total_orig_price)
                    print "total from " +str(total_markup) + " plus markup " + str(markup)
                    total_markup += markup
                    print "comes " + str(total_markup)
                    %>
        <td align='right' >${g.currency(markup)}</td>
        </tr>
    </td>
</ul>
</tr>
            %endfor
            <%
            cnt += 1
            %>
        %endif
    %endfor
<ul>
    <td>
        <tr>
        <td>Weekly markup</td>
        <td>&nbsp - &nbsp</td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td style="border-top:1px solid;">P</td>
        <td align='right' style="border-top:1px solid;">${g.currency(total_markup)}</td>
        </tr>
    </td>
</ul>
</table>


<br>
    <%
    week_total_markup += total_markup
    total_markup=0
    %>
%endfor
<br><br><br>
<ul>
    <td>
        <tr>
        <td>Total markup for the month</td>
        <td>&nbsp;-&nbsp;</td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td>&nbsp;&nbsp;&nbsp;&nbsp;</td>
        <td>P</td>
        <td align='right' style="border:1px solid #828633;">${g.currency(week_total_markup)}</td>
        </tr>
    </td>
</ul>
</div>

