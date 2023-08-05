__all__ = ['Item', 'Variant', 'Category', 'User', 'Cart', 'Address', 'Invoice']

import re
from myghty.util import *

class ModelSupertype(object):pass

class Item(ModelSupertype):
    def __init__(self, name, description, image, price, variants = None):
        self.name = name
        self.description = description
        self.image = image
        self.price = price
        
        self.variants = {}
        if variants is not None:
            for v in variants:
                list = self.variants.setdefault(v.categoryname, OrderedDict())
                list[v.name] = v

    def get_variant_categories(self):
        return self.variants.keys()
        
    def get_variant(self, categoryname, name):
        try:
            return self.variants[categoryname][name]
        except KeyError:
            return None
            
    def __eq__(self, other):
        return other.name == self.name

    def __ne__(self, other):
        return not self.__eq__(other)

class Variant(ModelSupertype):
    def __init__(self, categoryname, name, price = None):
        self.categoryname = categoryname
        self.name = name
        self.price = price
        
    def __eq__(self, other):
        return (
            self.categoryname == other.categoryname
            and self.name == other.name
            )

    def __ne__(self, other):
        return not self.__eq__(other)

class Category(ModelSupertype):
    def __init__(self, name, description, items, parent = None):
        self.name = name
        self.description = description
        self.items = items
        self.subcategories = OrderedDict()
        self.parent = parent
        
        self.path = '/%s' % self.name
        if self.parent is not None:
            self.path = parent.path + self.path
            self.parent.subcategories[self.name] = self
            self.root = self.parent.root
        else:    
            self.allitems = {}
            self.root = self
        
        for item in items:
            if not hasattr(item, 'primarycategory'):
                item.primarycategory = self
                self.root.allitems[item.name] = item

    def get_item(self, name):
        return self.root.allitems[name]
        
    def get_path(self):
        return self.path
        
    def get_category(self, path):
        match = re.match(r'/([^/]*)(/.*)?', path)
        
        (token, remainder) = match.group(1, 2)

        if not token: return self
        
        c = self.subcategories[token]
        
        if not remainder: return c
        else: return c.get_category(remainder)
        
    def get_categories(self):
        return iter(self.subcategories)
            
    def __str__(self):
        return self.name
        
class User(ModelSupertype):
    def __init__(self, username = None, email = None):
        self.username = username
        self.email = email
        self.addresses = []
        self.cart = None
        self.invoice = None

class Cart(ModelSupertype):
    def __init__(self):
        self.items = []
    
    def add_item(self, item, quantity, variants = []):
        for i in self.items:
            if i.equals(item, variants):
                i.quantity += quantity
                return

        self.items.append(CartItem(item, quantity, variants))
    
    def remove_item(self, index):
        self.items[index:index + 1] = []
                                
    def get_total(self):
        sum = 0
        for i in self.items:
            sum += i.get_total_price()
        return sum

    def is_empty(self):
        return len(self.items) == 0
        
class CartItem(ModelSupertype):
    def __init__(self, item, quantity, variants):
        self.item = item
        self.variants = dict([(v.categoryname, v) for v in variants])
        self.quantity = quantity

        self.price = item.price        
        for v in self.variants.values():
            if v.price is not None:
                self.price = v.price

    def get_variant_categories(self):
        return self.variants.keys()
    
    def get_variant(self, categoryname):
        try:
            return self.variants[categoryname]
        except KeyError:
            return None
    
    def get_item_price(self):
        return self.price
        
    def get_total_price(self):
        return self.quantity * self.price
                    
    def equals(self, item, variants):
        if self.item != item:
            return False
            
        for variant in variants:
            try:
                if self.variants[variant.categoryname] != variant:
                    return False
            except KeyError:
                return False
        
        return True
                
    def __eq__(self, other):
        return self.equals(other.item, other.variants.values())

    def __ne__(self, other):
        return not self.__eq__(other)
                
class Address(ModelSupertype):
    def __init__(self, firstname = None, 
               lastname = None, 
               street1 = None, 
               street2 = None, 
               city = None, 
               state = None, 
               zipcode = None, 
               country = None):
        self.street1 = street1
        self.street2 = street2
        self.firstname = firstname
        self.lastname = lastname
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.country = country
        
    def __eq__(self, other):
        for key in ('firstname', 'lastname', 'street1',
            'street2', 'city', 'state', 'zipcode', 'country'):
            if (not hasattr(other, key) 
                or getattr(other, key) != getattr(self, key)):
                return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)
        

class CreditCard(ModelSupertype):
    def __init__(self, ccname = None, cctype = None, ccnumber = None, ccexp = None):
        self.ccname = ccname
        self.cctype = cctype
        self.ccnumber = ccnumber
        self.ccexp = ccexp
    
    def _hiddencc(self):
        return ((len(self.ccnumber) - 5) * 'X') + self.ccnumber[-4:len(self.ccnumber)]
        
    hiddencc = property(_hiddencc)
    
class Invoice(ModelSupertype):
    def __init__(self, items, user, billingaddress = None, shippingaddress = None, creditcard = None):
        self.items = items
        self.user = user
        self.billingaddress = billingaddress
        self.shippingaddress = shippingaddress
        self.creditcard = creditcard
        
    def get_total(self):
        sum = 0
        for i in self.items:
            sum += i.get_total_price()
        return sum
