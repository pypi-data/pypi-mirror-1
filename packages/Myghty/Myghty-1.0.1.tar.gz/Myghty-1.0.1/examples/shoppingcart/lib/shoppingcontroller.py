import posixpath as unixpath
import myghty.component as component
import myghty.escapes as escapes
import re, os
import shoppingdata, shoppingmodel, form
from statemachine import *
import highlight

# shopping cart commands
CMD_ADD = 'add'
CMD_UPDATE = 'update'
CMD_REMOVE = 'remove'
CMD_NEXT = 'next'
CMD_PREVIOUS = 'previous'

# checkout process states
# the numbers are so they can be compared for ordering
CHECKOUT_START = '1_start'
CHECKOUT_BILLING = '2_billing'
CHECKOUT_SHIPPING = '3_shipping'
CHECKOUT_PAYMENT = '4_payment'
CHECKOUT_CONFIRM = '5_confirm'
CHECKOUT_DONE = '6_done'


## module components ##

class _Store(object):

    def do_component_init(self, component):
        self.store_path = component.interpreter.attributes.get('store_path')

    def catalog(self, m):
        """catalog component, parses the path and displays product list pages"""
        app = _RequestHelper(m, self)
        match = re.match(r".*/catalog/(.*/)?$", m.request_path)
        if not match:
            m.abort(404)

        path = match.group(1)
        if path is not None:
            path = escapes.url_unescape(path)

        category = shoppingdata.store

        if path:
            try:
                category = category.get_category('/' + path)
            except KeyError:
                m.abort(404)

        if len(category.items) > 0:
            items = category.items
        else:
            items = shoppingdata.featureditems.items

        app.show_template("catalog.myt", category = category, items = items)

    def item(self, m):
        """item component, parses the path and displays individual item pages"""
        match = re.match(r".*/item/(.*)/?$", m.request_path)
        itemname = match.group(1)

        if itemname is not None:
            itemname = escapes.url_unescape(itemname)

        try:
            item = shoppingdata.store.get_item(itemname)
        except KeyError:
            m.abort(404)

        _RequestHelper(m, self).show_template("item.myt", category = item.primarycategory, item = item)

    def cart(self, m, ARGS, cmd = None, qty = None, itemname = None, index = None):    
        """cart component, displays the shopping cart and handles updates"""
        app = _RequestHelper(m, self)
        save = False
        user = app.get_user()
        if user.cart is None:
            user.cart = shoppingmodel.Cart()
            save = True

        if itemname is not None:
            item = shoppingdata.store.get_item(itemname)
            variants = []
            for category in item.get_variant_categories():
                variants.append(item.get_variant(category, ARGS['variant_' + category]))

        if cmd == CMD_ADD:
            try:
                user.cart.add_item(item, int(qty), variants)
                save = True
            except ValueError:
                pass
        elif cmd == CMD_UPDATE:
            for i in range(0, len(user.cart.items)):
                try:
                    user.cart.items[i].quantity = int(ARGS['qty_' + str(i)])
                except ValueError:
                    pass
            save = True
        elif cmd == CMD_REMOVE:
            try:
                user.cart.remove_item(int(index))
                save = True
            except ValueError:
                pass

        if save:
            app.save_session()

        app.show_template("cart.myt", cart=user.cart)

    def checkout(self, m, ARGS, cmd = None, **params):
        """manages the checkout process, including form field handling and state transition.
        Delegates most of the work onto a CheckoutTransitions object which handles state transitions."""
        app = _RequestHelper(m, self)
        smachine = _CheckoutTransitions(app)
        smachine.do_transition(cmd)

        if smachine.template is not None:
            app.save_session()
            app.show_template(smachine.template, ck_state = smachine.state, form = smachine.form, invoice = smachine.invoice)


    def source(self, m, r):            
        """view source component, opens the source file up and displays.
        clearly, one should be careful with the configuration of this type of component 
        lest it be too flexible in what it shows.
        """

        filename = r.filename

        if os.path.isdir(filename):
            m.abort(403)

        try:
            f = file(filename)
        except IOError:
            m.abort(404)

        r.content_type = 'text/html'        
        s = f.read()
        s = highlight.highlight(s, filename = filename)

        _RequestHelper(m, self).show_template("viewsource.myt", name = m.request_path, source = s)


index = _Store()


class _RequestHelper(object):
    """a per-request helper object that performs common functions using the request object as well
    as the session."""
    def __init__(self, m, handler):
        self.m = m
        self.handler = handler

        session = m.get_session()

        if not session.has_key('shopping_user'):
            user = shoppingmodel.User()
            session['shopping_user'] = user
            session.save()

    def get_user(self):
        return self.m.get_session()['shopping_user']

    def save_session(self):
        self.m.get_session().save()

    def show_template(self, template, **params):
        self.m.subexec(self.handler.store_path + '/' + template, **params)



class _CheckoutTransitions(StateMachine):
    """
    a StateMachine implementation storing all the possible transitions for the shopping cart.
    
    the state itself is stored in the session and is also matched against a hidden form variable.
    if the two don't match, no transition occurs.
    
    this approach insures that the state of the checkout is determined by the server and
    cannot be overridden by a fabricated HTTP request.  It also renders any errors 
    related to the "reload" button irrelevant.  users can go 
    back/next/reload till the sun comes down on any checkout page and
    it wont screw up their state/submit twice/etc.
    """
    
    def __init__(self, app):
        self.app = app
        self.ARGS = app.m.request_args
        self.user = app.get_user()
        self.invoice = None            
        self.session = app.m.get_session()

    def create_form(self):
        """returns a Form object representing all the fields we are going to collect.
        the Form is stored in the users session."""
        
        return form.Form('checkout',
        [
            form.FormField('ck_state', default=CHECKOUT_START),
            form.FormField('currentform'),
            
            form.SubForm('billing', [
                form.IntFormField('useaddress', options = []),
                form.FormField('firstname', description = "First Name", required=True),
                form.FormField('lastname', description = "Last Name", required=True),
                form.FormField('street1', description = "Street", required=True),
                form.FormField('street2', description = "Street"),
                form.FormField('city', description = "City", required=True),
                form.FormField('state', description = "State", required=True),
                form.FormField('zipcode', description = "Zip Code", required=True),
                form.FormField('country', descriptinon = "Country", required=True, default='USA'),
            ]),
            
            form.SubForm('shipping', [
                form.IntFormField('useaddress', options = []),
                form.FormField('firstname', description = "First Name", required=True),
                form.FormField('lastname', description = "Last Name", required=True),
                form.FormField('street1', description = "Street", required=True),
                form.FormField('street2', description = "Street"),
                form.FormField('city', description = "City", required=True),
                form.FormField('state', description = "State", required=True),
                form.FormField('zipcode', description = "Zip Code", required=True),
                form.FormField('country', descriptinon = "Country", required=True, default='USA'),
                
            ]),
            
            form.SubForm('payment', [
                form.FormField('ccname', description="Credit Card Name", required = True, textsize=40),
                form.FormField('cctype', description = "Credit Card Type", required = True, options=(
                                        ('amex', 'American Express'),
                                        ('visa', 'Visa'),
                                        ('mastercard', 'Master Card'),
                                        )),
                form.CCFormField('ccnumber', description ="Credit Card Number", required = True, textsize=20, default = '371449635398431'),
                form.DateFormField('ccexp', description ="Credit Card Expiration Date", required = True, fields = ['month', 'year'], yeardeltas = range(0, 9)),
            ]),
        ])


    def do_transition(self, transition):

        if not self.session.has_key('invoice_form') or transition is None:
            self.state = CHECKOUT_START
            self.invoice_form = self.create_form()
            self.session['invoice_form'] = self.invoice_form
        else:
            self.invoice_form = self.session['invoice_form']
            self.state = self.invoice_form.elements['ck_state'].displayvalue
            self.set_current_form(self.invoice_form.elements['currentform'].displayvalue)
            
            if self.state >= CHECKOUT_CONFIRM:
                self.template = 'confirm.myt'
                self.invoice = self.user.invoice
            else:
                self.template = 'checkout.myt'
            
            if self.state != self.ARGS['ck_state'] or self.state == CHECKOUT_DONE:
                return
        
        if transition is None:
            transition = CMD_NEXT
        
        try:
            self.state = StateMachine.do_transition(self, self.state, transition)
            self.invoice_form.elements['ck_state'].set_value(self.state)
        except AbortTransition: pass

    def set_current_form(self, name):
        self.invoice_form.elements['currentform'].set_value(name)
        self.form = self.invoice_form.elements[name]

    def set_address_dropdowns(self):
        addresses = [(i, self.user.addresses[i].street1) for i in range(0, len(self.user.addresses))]

        if len(addresses):
            addresses.insert(0, ('', 'select an address'))

            self.invoice_form.elements['billing'].elements['useaddress'].options = addresses
            self.invoice_form.elements['shipping'].elements['useaddress'].options = addresses
        
    def extract_address(self):
        address = shoppingmodel.Address()
        self.form.reflect_to(address)
        for a in self.user.addresses:
            if address == a: break
        else:
            self.user.addresses.append(address)
        self.set_address_dropdowns()
        return address

    def fill_address(self):
        address = self.user.addresses[self.form.elements['useaddress'].currentvalue]
        self.form.elements['useaddress'].set_value(None)
        self.form.reflect_from(address)
        self.form.unvalidate()
        return address
        
    def start_to_billing(self):
        self.set_address_dropdowns()
        self.set_current_form('billing')
        self.template = 'checkout.myt'
        
    def billing_to_start(self):
        self.app.show_template("cart/")    
        self.template = None

    def billing_to_shipping(self):
        self.form.set_request(self.ARGS)

        if self.form.elements['useaddress'].currentvalue is not None:
            address = self.fill_address()
            self.set_current_form('shipping')
            self.form.unvalidate()

        elif self.form.is_valid():
            self.extract_address()
            self.set_current_form('shipping')
            self.form.unvalidate()
        else:
            raise AbortTransition()

    def shipping_to_billing(self):
        self.set_current_form('billing')
        self.form.unvalidate()

    def shipping_to_payment(self):
        self.form.set_request(self.ARGS)

        if self.form.elements['useaddress'].currentvalue is not None: 
            address = self.fill_address()
            ccname = address.firstname + " " + address.lastname
            
            self.set_current_form('payment')
            self.form.elements['ccname'].set_value(ccname)
            self.form.unvalidate()
        elif self.form.is_valid():
            address = self.extract_address()
            ccname = address.firstname + " " + address.lastname
            
            self.set_current_form('payment')
            self.form.elements['ccname'].set_value(ccname)
            self.form.unvalidate()
        else:
            raise AbortTransition()
            
        
    def payment_to_shipping(self):
        self.set_current_form('shipping')
        self.form.unvalidate()

    def payment_to_confirm(self):
        self.form.set_request(self.ARGS)

        if self.form.is_valid():
            billing= shoppingmodel.Address()
            self.invoice_form.elements['billing'].reflect_to(billing)

            shipping = shoppingmodel.Address()
            self.invoice_form.elements['shipping'].reflect_to(shipping)

            cc = shoppingmodel.CreditCard()
            self.invoice_form.elements['payment'].reflect_to(cc)

            invoice = shoppingmodel.Invoice(self.user.cart.items, self.user, billing, shipping, cc)

            self.user.invoice = invoice
            self.invoice = invoice
            
            self.template = 'confirm.myt'
        else:
            raise AbortTransition()

    def confirm_to_payment(self):
        self.set_current_form('payment')
        self.template = 'checkout.myt'
        self.form.unvalidate()
        
    def confirm_to_done(self):
        self.invoice = self.user.invoice
        self.user.cart.items = []
        self.template = 'confirm.myt'
    
    transitions = dict([
        Transition(CHECKOUT_START, CHECKOUT_BILLING, CMD_NEXT, start_to_billing),
        Transition(CHECKOUT_BILLING, CHECKOUT_START, CMD_PREVIOUS, billing_to_start),
        Transition(CHECKOUT_BILLING, CHECKOUT_SHIPPING, CMD_NEXT, billing_to_shipping),
        Transition(CHECKOUT_SHIPPING, CHECKOUT_BILLING, CMD_PREVIOUS, shipping_to_billing),
        Transition(CHECKOUT_SHIPPING, CHECKOUT_PAYMENT, CMD_NEXT, shipping_to_payment),
        Transition(CHECKOUT_PAYMENT, CHECKOUT_SHIPPING, CMD_PREVIOUS, payment_to_shipping),
        Transition(CHECKOUT_PAYMENT, CHECKOUT_CONFIRM, CMD_NEXT, payment_to_confirm),
        Transition(CHECKOUT_CONFIRM, CHECKOUT_PAYMENT, CMD_PREVIOUS, confirm_to_payment),
        Transition(CHECKOUT_CONFIRM, CHECKOUT_DONE, CMD_NEXT, confirm_to_done),
    ])
        




