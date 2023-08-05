<%attr>
	context='login'
	title = 'Login'
</%attr>

<%args>
	failed = None
</%args>

<form method="post" action="/login/">
<table>
	<tr>
		<td>Username:</td>
		<td><input type="text" name="username"> ('testuser')</td>
	</tr>
	<tr>
		<td>Password:</td>
		<td><input type="password" name="password"> ('password')</td>
	</tr>
	<tr>
		<td><input type="submit"></td>

% if failed is True:
		<td>
	<span class="red">Login failed !</span>
		</td>
%
	</tr>
</table>
</form>
