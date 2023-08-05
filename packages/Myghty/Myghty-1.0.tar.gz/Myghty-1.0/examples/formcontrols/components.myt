
<%method textfield>
	<%args>
		name
		value = None
	</%args>
<input type="text" name="<% name %>" value="<% value %>">
</%method>

<%method textarea>
	<%args>
		name
		value = None
	</%args>
<textarea name="<% name %>"><% value |h%></textarea>
</%method>


<%method select>
	<%args>
		name
		options
	</%args>
<select name="<% name %>">
% for option in options:
	<option value="<% option['id'] %>"><% option['description'] %></option>
% # end
</select>
</%method>

<%method button>
	<%args>
		name
		label
		onclick
	</%args>
<input type="button" value="<% label %>" name="<% name %>" onClick="<% onclick %>">
</%method>
