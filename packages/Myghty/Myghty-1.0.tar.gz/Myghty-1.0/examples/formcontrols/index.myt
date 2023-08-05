<%args>
	fname = None
	lname = None
	address = None
	comments = None
</%args>


<form method="post" action="index.myt">
<table>
	<&|field.myt, label="First Name"&>
		<&components.myt:textfield, name="fname",  value=fname &>
	</&>
	<&|field.myt, label="Last Name"&>
		<&components.myt:textfield, name="lname", value=lname &>
	</&>
	<&|field.myt, label="Address"&>
		<&components.myt:textfield, name="address", value=address &>
	</&>
	<&|field.myt, label="Comments"&>
		<&components.myt:textarea, name="comments", value=comments &>
	</&>

	<tr><td>
		<& components.myt:button, label="go", name="go", onclick="form.submit()" &>
	</td></tr>
</table>

</form>


name: <% fname %> <% lname %><br/>
address: <% address %><br/>
comments:

% if comments is not None:
<% comments %>
%


<%method title>
Myghty Examples - Form Controls
</%method>
