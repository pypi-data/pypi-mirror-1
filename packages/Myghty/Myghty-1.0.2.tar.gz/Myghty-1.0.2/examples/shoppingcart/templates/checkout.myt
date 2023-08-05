<%python scope="global">
	import shoppingmodel, shoppingcontroller
</%python>

<%args>
	form
	ck_state
</%args>


<span class="headertext1">Checkout</span>

<& breadcrumb, form = form, ck_state=ck_state &>


<&| forms.myc:form, name="checkout", action="checkout/" &>

	<input type="hidden" name="cmd" value="<% shoppingcontroller.CMD_NEXT %>" >
	<input type="hidden" name="ck_state" value="<% ck_state %>" >

% if ck_state==shoppingcontroller.CHECKOUT_BILLING or ck_state==shoppingcontroller.CHECKOUT_SHIPPING:

	<& existingaddress, form = form &>
	
	<div class="checkoutbox">
	<& address.myc, form=form &>
	<& go &>
	</div>
	
% elif ck_state == shoppingcontroller.CHECKOUT_PAYMENT:

	<div class="checkoutbox">
	<& ccard.myc, form=form &>
	<& go &>
	</div>
% else:
 	whoops, todo !
 	state: <% ck_state %>
	<& go &>
%

</&>

<%def existingaddress>
	<%args>form</%args>
% 	if len(form.elements['useaddress'].options):
		<div class="checkoutbox">
		<span class="cartheader">Use existing address:</span>
		<& forms.myc:select, field=form.elements['useaddress'] &><br/>
		<& go &>
		</div>
%	
</%def>


<%method breadcrumb>
	<%args>
		form = None
		ck_state
	</%args>

	<div class="breadcrumb">
	<span class="headertext3">
	<&|stepname, state=shoppingcontroller.CHECKOUT_BILLING, ck_state = ck_state, form=form&>Billing Address</&> -&gt; 
	<&|stepname, state=shoppingcontroller.CHECKOUT_SHIPPING, ck_state = ck_state, form=form&>Shipping Address</&> -&gt; 
	<&|stepname, state=shoppingcontroller.CHECKOUT_PAYMENT, ck_state = ck_state, form=form&>Payment</&> -&gt; 
	<&|stepname, state=shoppingcontroller.CHECKOUT_CONFIRM, ck_state = ck_state, form=form&>Confirm</&>
	</span>
	</div>
</%method>

<%method stepname trim="both">
	<%args>
		state
		ck_state
		form = None
	</%args>

% if ck_state > state:
	<span style="color:green">
% elif ck_state == state:
%	if form is not None and form.is_valid() is False:
		<span style="color:red;font-weight:bold">
%	else:
		<span style="color:blue;font-weight:bold">
%
% else:
	<span>
%
<% m.content() %>
</span>
</%method>

<%method go>
	<br/>
	<center>
	<& forms.myc:submit, value="&lt;&lt;&lt; Previous", onclick="document.checkout.cmd.value='%s'" % shoppingcontroller.CMD_PREVIOUS &>
	<& forms.myc:submit, value="Next &gt;&gt;&gt;" &>
	</center>
</%method>

