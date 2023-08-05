<%args>
	cart
</%args>
<%global>
	import shoppingcontroller
</%global>

% if cart.is_empty():
	<div class="headertext2">There are no items in your shopping cart.</div>
	
	<a href="<& common.myc:store_uri &>catalog/">Keep shopping!</a>
%    return
%

<&| forms.myc:form, action="cart/", name="cartform" &>
<input type="hidden" name="cmd" value="<% shoppingcontroller.CMD_UPDATE %>">
<div class="headertext2">Your Shopping Cart</div>
<table>
<tr>
	<td class="cartheader">Quantity</td>
	<td class="cartheader">Item</td>
	<td class="cartheader">Style</td>
	<td class="cartheader">Price Per Item</td>
	<td class="cartheader">Total Price</td>
	<td></td>
</tr>
% index = 0
% for cartitem in cart.items:
	<tr>
		<td><& forms.myc:text, value=cartitem.quantity, size=2, name="qty_" + str(index) &></td>
		<td><& common.myc:item_link, item = cartitem.item &></td>
		<td>
%	for variant in cartitem.variants.values():
			<% variant.categoryname %>: <% variant.name %>
% 
		</td>
		<td>
		<& common.myc:price, price = cartitem.get_item_price() &>
		</td>
		<td>
		<& common.myc:price, price = cartitem.get_total_price() &>
		</td>
		<td>
			<a href="<& common.myc:store_uri &>cart/?cmd=<% shoppingcontroller.CMD_REMOVE %>&index=<% repr(index) %>" class="smalllink">(remove)</a>
		</td>
	</tr>
%	index +=1
%

	<tr>
	<td><& forms.myc:button, value="update", cssclass="smallbutton", onclick="cartform.submit()" &></td>
	</tr>

	<tr>
		<td colspan="4" class="cartheader" align="right">Total:</td>
		<td><b><& common.myc:price, price = cart.get_total() &></b></td>
	</tr>

	<tr>
	<td align=="left" colspan="2">
	<a href="<& common.myc:store_uri &>catalog/"><b>&lt;&lt;&lt; Continue Shopping</b></a>
	</td>
	
	<td align="right" colspan="3">
	<a href="<& common.myc:store_uri &>checkout/"><b>Go To Checkout &gt;&gt;&gt;</b></a>
	</td>
	</tr>

</table>


</&>