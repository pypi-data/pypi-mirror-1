
<%args>
	category
	items
	columns = 2
</%args>

<%python scope="init">
	# cache the contents of the component, keyed off of category path.
	# component will be executed at most every 120 seconds for a given 
	# category.
	if m.cache_self(key=category.get_path(), cache_expiretime=120):
		return
</%python>

<& breadcrumb.myc, category = category &>

<table cellspacing="0" cellpadding="0">
% index = 0
% while index < len(items):

	<tr>
% 	for i in range(0, columns):
%		if index >= len(items): break
%		else: item = items[index]

<td valign="top" class="categoryitemcell">

	<& common.myc:item_image, item=item &>

	<div class="categoryitemname">
		<& common.myc:item_link, item=item &>
		<br/>
		<% item.price %>	
	</div>
</td>
%		index +=1
%
	</tr>
%
</table>

