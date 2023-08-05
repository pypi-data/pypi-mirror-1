<%doc>
	in this page, the first argument to the resulting 
	javascript function must be the DOM id
	with which to write the resulting html, which is 
	because it specifies 'writedom' as the type of delivery, 
	but no 'dom_id' argument.  the second argument to the javscript 
	function is specified as the only component argument below, 
	which is the message to be displayed.
</%doc>
<%attr>
	 type='writedom'
</%attr>
<%args>
	message
</%args>

<% message %>
<img src='hourglass.gif' />
 
 
 
