

<%doc>
	first, we define all the various AJAX methods we want to call,
	and register them with the myghtyjax handler.  all of these functions,
	as well as the myghtyjax initializer functions, can  
	be anywhere, at the bottom of the whole page or even in a totally different file,
	and also shared by any number of templates.
</%doc>


<%once>
	# a plain python function which will be mapped to a javascript function
	def myresult (firstname, lastname, email):
		return "document.getElementById('result').innerHTML = 'well hi %s %s %s';" % (firstname, lastname, email)
</%once>

<%doc>
	a myghty "hello" method that will be mapped to a javascript function
</%doc>
<%method myres>
	<%args>
		firstname
		lastname
	</%args>
	
	document.getElementById('result').innerHTML = "hello <% firstname %> <%lastname %>!";
</%method>

<%doc>
	a myghty "hello" method whos HTML contents will be returned to a callback function.
	note that you can also call this component within the original template (or from any
	other template), not just via XMLHttpRequest.  This illustrates multi-contextual 
	templating components.
</%doc>
<%method drawtable>
	<%attr>
		type='source'
	</%attr>
	<%args>
		firstname
		lastname
		email
	</%args>

	<table border="1">
		<tr>
			<td><b>First</b></td>
			<td><b>Last</b></td>
			<td><b>Email</b></td>
		</tr>
		<tr>
			<td><% firstname %></td>
			<td><% lastname %></td>
			<td><% email %></td>
		</tr>
	</table>
</%method>


<%doc>
	a myghty method to add two numbers, and the resulting HTML contents
	will be drawn directly to a DOM element.
	Includes an optional argument "slow" which will cause it to 
	pause 2 seconds.  while pointless here, it is meant to simulate an 
	operation that might be doing a long database operation or something 
	similarly time-consuming.
</%doc>
<%method addnumbers>
	<%args>
		leftop
		rightop
		slow = False
	</%args>
	<%attr>
		type='writedom'

		# specify a fixed target DOM id.  if 
		# omitted, the target id must be specified
		# as the first argument to the javascript 
		# function.
		dom_id='addresult'
	</%attr>
	<%init>
		import time
		if slow: 
			time.sleep(2)

		try:
			a = str(int(leftop) + int(rightop))
		except:
			a = ''

	</%init>
	
%	if slow:
		After much consideration, I can safely say that
		<% leftop %> + <% rightop %> = <% a %> !
%	else:
		<% a %> !  that was easy.
%
</%method>




<%init>
	# register the functions with myghtyjax.
	# if this function returns True, it means myghtyjax
	# executed the ajax-enabled component, so we return
	# from execution.

	# note that autohandlers are not executed within the 
	# ajax call, as myghtyjax.myt, the entry point for
	# all XMLHttpRequest calls, inherits from None.
	if m.comp('myghtyjax.myt:init', 
		# local python def
		myresult = myresult, 
		
		# local myghty methods	
		add = 'SELF:addnumbers',
		myres = 'SELF:myres',
		drawtable = 'SELF:drawtable',

		# an external template
		hourglass = 'hourglass.myt',
		): return

</%init>

<%doc>Deliver the myghtyajax javascript stub functions.  This method takes 
the optional arguments 'handleruri' and 'scripturi', which reference the 
web-addressable URI of the myghtyjax.myt file and the myghtyjax.js file.  They
can also be set as global interpreter attributes.  If not supplied, myghtyjax
determines them based on where it is being called from.
</%doc>
<& myghtyjax.myt:js &>






<h2>Myghty Ajax Toolkit</h2>

<p>
	In this example, Myghty is used to create a seamless bridge between client-side Javascript and server-side Python functions, or between Javascript and Myghty template components.  You can write regular Python-embedded HTML, put a set of tags around it, and have that component's server-side code and textual output "magically" become available as a regular javascript function, which can return its text, execute server-generated Javascript, or write its output into any DOM element on the page.

</p>
<a href="/source/examples/myghtyjax/index.myt">index.myt</a>  - this page illustrates various functions that utilize myghtyjax<br/>
<a href="/source/examples/myghtyjax/hourglass.myt">"hourglass" page</a> - this page illustrates how functions can exist in a second page<br>
<a href="/source/examples/myghtyjax/myghtyjax.myt">myghtyjax library</a> / 
<a href="/source/examples/myghtyjax/myghtyjax.js">javascript functions</a> - this is the actual library

<br/>
<br/>
Try out the functions here.  Each click of a button generates a request to the server, whose output is then populated into the current page:<br/>

<form method="post" name="mainform">
	<table>

	<tr><td></td><td></td>
	<td rowspan="3"><span id="result"></span></td></tr>

	<tr><td>First Name:</td><td><& text, name="firstname", value="wile e"&></td></tr>
	<tr><td>Last Name:</td><td><& text, name="lastname", value="coyote"&></td></tr>
	<tr><td>Email:</td><td><& text, name="email", value="wilee@suprgenius.net"&></td></tr>

	<tr><td colspan="2">
	<input type="button" value="Call Python Def" onClick="myresult(
		document.mainform.firstname.value,
		document.mainform.lastname.value,
		document.mainform.email.value)">

	<input type="button" value="Call Myghty Method" onClick="myres(
		document.mainform.firstname.value,
		document.mainform.lastname.value,
		document.mainform.email.value)">

	<input type="button" value="Draw a Table" onClick="drawtable(
		function(x) {document.getElementById('result').innerHTML = x;},
		document.mainform.firstname.value,
		document.mainform.lastname.value,
		document.mainform.email.value)">

	<br/><br/>
	</td></tr>
	</table>

	<& text, name="leftop", value="4", size=3 &> + <& text, name="rightop", value="5", size=3 &> = <span id="addresult"></span>
	
	<br/>	
	<input type="button" value="Add" onClick="add(
		document.mainform.leftop.value,
		document.mainform.rightop.value)">

# 	for the "slow" version, we call the "hourglass" function first. 
	<input type="button" value="Add Slowly" onClick="hourglass('addresult', 'Adding these numbers...whew.....');add(
		document.mainform.leftop.value,
		document.mainform.rightop.value, 1)">
	
</form>


<%method text>
	<%args>
		name
		size=20
		value = None
	</%args>
	<input type="text" name="<% name %>" size="<% size %>" value="<% value or m.request_args.get(name, None) %>" >
</%method>


