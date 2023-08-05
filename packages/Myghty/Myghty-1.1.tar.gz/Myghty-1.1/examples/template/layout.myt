<%doc>
	layout.myt, regular layout
</%doc>

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

	<div class="header">
		<% header %>
	</div>

	<div class="left-column">
		<% leftnav %>
	</div>

	<div class="content-body">
		<% body %>
	</div>


	<div class="footer">
		<% footer %>
	</div>
</body>
</html>


