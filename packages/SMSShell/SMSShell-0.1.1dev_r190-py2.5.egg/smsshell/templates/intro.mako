<%doc>
blank.mako - Blank Template for SMSShell application

AUTHOR: Emanuel Gardaya Calso <egcalso@gmail.com>

Modification Dates:
    2008-04-03

</%doc>
<%inherit file="base.mako"/>

<%
%>

<div id="intro-page">
##<img src="${g.base_url}/img/smsshell.png" alt="SMS Shell" width="480px" />
<h1> SMS Shell </h1>

<div class="content">
<h2>Getting Started</h2>
<dl>

<dt>
<a href="#" onclick="show_hide('dLabel')">Labels</a>
</dt>
<dd id="dLabel">
<p>Labels that can be applied to messages.</p>
<p>These can be applied automatically thru filters or manually in the message list.</p>
</dd>

<dt>
<a href="#" onclick="show_hide('dFilter')">Filters</a>
</dt>
<dd id="dFilter">
<p>Rules to filter messages &mdash; labelling them or assigning actions to them.</p>
<p>The actions can be <strong>reply</strong>, <strong>visit</strong> or <strong>run</strong>.</p>
</dd>

<dt>
<a href="#" onclick="show_hide('dResponse')">Response</a>
</dt>
<dd id="dResponse">
<p>Automated response based on keywords.</p>
<p>You can give options to <em>search</em>, <em>add</em> entries, <em>edit</em> an entry or <em>delete</em> an entry from a selection of <strong>tables</strong>.</p>
<p>The list of <strong>arguments</strong> are those that you expect the sender to give when searching, adding or editing.</p>
<p>After receiving a message with a matching keyword, the system will send a reply with the result from the expected action.</p>
</dd>

<dt>
<a href="#" onclick="show_hide('dCompose')">Compose</a>
</dt>
<dd id="dCompose">
<p>Create a new message.</p>
<p>By default, the system sends the message you created as soon as the sending queue is free. However, you can also schedule a message to be sent on a future time by providing a schedule.</p>
</dd>

<dt>
<a href="#" onclick="show_hide('dEstate')">Estates</a>
</dt>
<dd id="dEstate">
<p>This is a sample database table to search from. It contains address details of different properties.</p>
</dd>

<dl>
</div>

</div>

