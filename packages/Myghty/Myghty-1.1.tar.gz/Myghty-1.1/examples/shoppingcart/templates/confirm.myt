<%python scope="global">
	import shoppingmodel, shoppingcontroller
</%python>

<%args>
	invoice
	ck_state
</%args>


<& checkout.myt:breadcrumb, ck_state = ck_state &>

% if ck_state == shoppingcontroller.CHECKOUT_DONE:
	<span class="headertext2">Order Complete - Thanks for your order !</span>
%

<&| forms.myc:form, name="checkout", action="checkout/" &>

<input type="hidden" name="cmd" value="<% shoppingcontroller.CMD_NEXT %>" >
<input type="hidden" name="ck_state" value="<% ck_state %>" >

<table width="95%">

	<tr><td colspan="2">

		<div class="borderbox">
		<span class="cartheader">Invoice</span>

		<& staticitems, invoice = invoice &>
		</div>	

	</td></tr>
	
	<tr><td>

		<div class="borderbox">
		<span class="cartheader">Billing Address</span>
		<& staticaddress, address = invoice.billingaddress &>
		</div>
	</td>
	<td>
		<div class="borderbox">
		<span class="cartheader">Shipping Address</span>
		<& staticaddress, address = invoice.shippingaddress &>
		</div>
	</td>
	</tr>

	<tr><td colspan="2">
		<div class="borderbox">
		<span class="cartheader">Payment Info</span>
		<& staticcc, cc = invoice.creditcard &>
		</div>
		
	</td></tr>
	</table>
	
% if ck_state == shoppingcontroller.CHECKOUT_CONFIRM:
	<& checkout.myt:go &>
%	
	</div>
</&>


<%def staticaddress>
	<%args>address</%args>
	<table>
		<tr><td>Name:</td><td><% address.firstname %> <%address.lastname %></td></tr>
		<tr><td>Street:</td><td><% address.street1 %><br/><% address.street2 %></td></tr>
		<tr><td>City:</td><td><% address.city %></td></tr>
		<tr><td>State:</td><td><% address.state %></td></tr>
		<tr><td>Zip:</td><td><% address.zipcode %></td></tr>
		<tr><td>Country:</td><td><% address.country %></td></tr>
	</table>
</%def>

<%def staticcc>
	<%args>cc</%args>
	<table>
		<tr><td>Name:</td><td><% cc.ccname %></td></tr>
		<tr><td>Number:</td><td><% cc.hiddencc %></td></tr>
		<tr><td>Type:</td><td><% cc.cctype %></td></tr>
		<tr><td>Exp:</td><td><% cc.ccexp%></td></tr>
	</table>	
</%def>


<%def staticitems>
	<%args>
	invoice
	</%args>
	
	<table width="95%">
	<tr>
		<td class="cartheader">Item</td>
		<td class="cartheader">Style</td>
		<td class="cartheader">Price</td>
		<td class="cartheader">Quantity</td>
		<td class="cartheader">Total</td>
	</tr>
	
%	for item in invoice.items:
	<tr>
		<td><% item.item.name %></td>
		<td>
%	for variant in item.variants.values():
			<% variant.categoryname %>: <% variant.name %>
% 
		</td>
		<td>
		<& common.myc:price, price = item.get_item_price() &>
		</td>
		<td>
			<% item.quantity %>
		</td>
		<td>
		<& common.myc:price, price = item.get_total_price() &>
		</td>
	</tr>	
%
	<tr>
		<td colspan="4" class="cartheader" align="right">Total:</td>
		<td><b><& common.myc:price, price = invoice.get_total() &></b></td>
	</tr>
	</table>
</%def>

