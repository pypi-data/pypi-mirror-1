<%args>
	firstname
	lastname
	occupation
</%args>

Thanks for registering, <% firstname %> <% lastname %>!  Please join the queue on your <% occupation == "programmer" and "left" or "right" %>.


<br/>

The args given to this page are: <% repr(ARGS) %>


<%method title>
Myghty Examples - Form Visitor
</%method>


