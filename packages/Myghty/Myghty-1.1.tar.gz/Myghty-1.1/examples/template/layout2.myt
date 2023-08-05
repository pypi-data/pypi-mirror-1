<%args>
        title 
        header
        leftnav
        body
        footer
</%args>

<html>
<head>
	<title><% title %></title>
	<link rel="stylesheet" href="style.css"></link>
</head>

<body>

	<div class="content-body">	
	<% header %>

	<div class="left-column" style="float:right;">
		<% leftnav %>
	</div>

	<% body %>

	<% footer %>
	</div>
</body>
</html>


