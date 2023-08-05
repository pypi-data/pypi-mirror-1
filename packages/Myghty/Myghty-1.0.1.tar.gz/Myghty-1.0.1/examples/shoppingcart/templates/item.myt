<%args>
	item
	category
</%args>

<%python scope="init">
	import shoppingcontroller
	
	# cache the contents of the component, keyed off of item name.
	# component will be executed at most every 120 seconds for a given
	# item.
	if m.cache_self(key=item.name, cache_expiretime=120):
		return
</%python>

<& breadcrumb.myc, category = category &>

<div class="item">
<&| forms.myc:form, action='cart/' &>
	<table>
	<tr>
	<td>
	<& common.myc:item_image, item=item &>
	</td>
	<td>
	<div class="itemdescription">
		<input type="hidden" name="cmd" value="<% shoppingcontroller.CMD_ADD %>">
		<input type="hidden" name="itemname" value="<% item.name %>">
		<span class="itemname"><% item.name %></span><br/>
		<% item.price %>
		<br/>
		
%		if item.variants is not None:
	<table cellpadding="0" cellspacing="0">
%		for key, list in item.variants.iteritems():
		<tr>
		<td class="variantname">
			<% key %>:
		</td>

		<td class="variantoptions">
		
# 		the call to create the select box of item variants 
#		is a little involved, which led me to cache this component
		<& forms.myc:select, name='variant_' + key, options=[(v.name, "%s%s" % (v.name, m.scomp('common.myc:price', price = v.price))) for v in list.values()] &>
	
		</td>

		</tr>
%
	</table>

%		
		<br/><br/>
		Add to Cart:
		<& forms.myc:text, size=2, name="qty", value="1" &> item(s) <& forms.myc:submit, value="go" &>
		
	</div>
	</td>
	</tr>
	<tr><td colspan="2" align="center">
		<a href="<& common.myc:category_uri, category=category&>">Back to category '<% category.description %>'</a>
	</td></tr>
	</table>
</&>
</div>


