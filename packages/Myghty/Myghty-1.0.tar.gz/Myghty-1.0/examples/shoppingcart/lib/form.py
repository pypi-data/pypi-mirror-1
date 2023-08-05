"""
    a set of classes that represent an HTML form, including its field names, 
    the values of those fields corresponding to their application setting
    as well as the value pulled from an HTTP request, and validation rules
    for the fields.  "hierarchical forms" can be created as well, allowing a form
    to be grouped into "subforms", which may live on the same HTML page or across
    several HTML pages.
"""

from myghty.util import *
import inspect, datetime, types

class FormElement:
    def __init__(self, name, **params):
        self.name = name
        self.description = ''

    def set_form(self, form):pass
    def set_request(self, req, validate = True):pass
    
    def is_valid(self):return None
    def unvalidate(self):pass
    def get_valid_message(self):return ''
    
class Form(FormElement):
    def __init__(self, name, elements, **params):
        FormElement.__init__(self, name)
        
        self.isvalid = None
        self.elements = OrderedDict()
        for elem in elements:
            self.elements[elem.name] = elem
            elem.set_form(self)

    def set_form(self, form):pass

    def show_default(self):[elem.show_default() for elem in self.elements.values()]
    def show_value(self):[elem.show_value() for elem in self.elements.values()]
    def show_request_value(self):[elem.show_request_value() for elem in self.elements.values()]

    def is_valid(self):
        return self.isvalid

    def get_valid_message(self):
        if self.isvalid:
            return "Form is valid"
        elif self.isvalid is False:
            return "Some fields could not be validated"
    
    def unvalidate(self):
        self.isvalid = None
        for elem in self.elements.values(): elem.unvalidate()
    
    def get_field(self, name):
        try:
            return self.elements[name]
        except KeyError:
            return None
        
    def set_request(self, req, validate = True):
        self.isvalid = True
        for elem in self.elements.values():
            elem.set_request(req, validate)
            if not elem.is_valid():
                self.isvalid = False
                
    def _fieldname(self, formfield):
        return formfield.name

    def reflect_from(self, object):
        for elem in self.elements.values():
            elem.reflect_from(object)
        
    def reflect_to(self, object):
        for elem in self.elements.values():
            elem.reflect_to(object)

    
class SubForm(Form):
        
    def _fieldname(self, formfield):
        return self.name + "_" + formfield.name
        
class FormField(FormElement):
    def __init__(self, name, description = None, required = False, default = None, textsize = None, options = None, **params):
        FormElement.__init__(self, name)

        if description is None:
            self.description = name
        else:
            self.description = description
        
        self.required = required
        self.options = options
        self.textsize = textsize

        # default value (any type)
        self.default = default
        
        # programmatically set value (any type)
        self.value = None
        
        # value taken from the request (any type)
        self.request_value = None
        
        # current used value (any type)
        self.currentvalue = default

        # string display value
        if self.currentvalue is None:
            self.displayvalue = ''
        else:
            self.displayvalue = str(self.currentvalue)
        
        
        self.displayname = None
        self.valid_message = ''        
        self.isvalid = None
        
    def set_form(self, form):
        self.displayname = form._fieldname(self)

    def set_value(self, value):
        self.value = value
        self.currentvalue = value
        if self.currentvalue is None:
            self.displayvalue = ''
        else:
            self.displayvalue = str(self.currentvalue)
    
    def show_default(self):self.displayvalue = self.default
    def show_value(self):self.displayvalue = self.value
    def show_request_value(self):self.displayvalue = self.request_value

    def reflect_to(self, object):
        if hasattr(object, self.name):
            setattr(object, self.name, self.displayvalue)

    def reflect_from(self, object):
        if hasattr(object, self.name):
            self.set_value(getattr(object, self.name))

    def is_valid(self):
        """returns whether or not this field is valid.  note that the 
        third state of None indicates this field has not been validated."""
        return self.isvalid

    def get_valid_message(self):
        return self.valid_message
        
    def set_request(self, request, validate = True):
        
        """sets the request for this form.   if validate is True, also 
        validates the value."""

        try:
            self.request_value = request[self.displayname]
        except KeyError:
            self.request_value = None
    
        if validate:
            if self.required and not self.request_value:
                self.isvalid = False
                self.valid_message = 'required field "%s" missing' % self.description
            else:
                self.isvalid = True
        
        if self.request_value is None:
            self.displayvalue = ''
        else:
            self.displayvalue = str(self.request_value)
            
        self.currentvalue = self.request_value
    
    def unvalidate(self):
        """resets the isvalid state of this form to None"""
        self.isvalid = None
        self.valid_message = ''
        

class IntFormField(FormField):
    def __init__(self, *args, **params):
        FormField.__init__(self, *args, **params)
        self.currentvalue = None
        
            
    def set_request(self, request, validate = True):
        FormField.set_request(self, request, validate)
        
        try:
            if self.currentvalue == '':
                self.currentvalue = None
                
            if self.currentvalue is not None:
                self.currentvalue = int(self.currentvalue)
        except ValueError:
            if self.isvalid and validate:
                self.valid_message = 'field "%s" must be an integer number' % self.description
                self.isvalid = False
                self.currentvalue = None
                
                
class CompoundFormField(SubForm):
    """
    a SubForm that acts like a single formfield in that it contains a single value,
    but also contains subfields that comprise elements of that value.
    
    examples: a date with year, month, day fields, corresponding to a date object
    
    more exotic examples: a credit card field with ccnumber, ccexpiration fields corresponding to a 
    CreditCard object, an address field with multiple subfields corresopnding to an Address object, etc.
    
    """

    def __init__(self, name, elements, description = None, **params):
        SubForm.__init__(self, name, elements, **params)
        self.value = None
        self.request_value = None
        self.displayvalue = None

        if description is None:
            self.description = name
        else:
            self.description = description
        
    def set_value(self, value):
        self.value = value
        self.currentvalue = value
        self.displayvalue = str(value)
        self.set_compound_values(value)        

    def reflect_to(self, object):
        if hasattr(object, self.name):
            setattr(object, self.name, self.currentvalue)

    def reflect_from(self, object):
        if hasattr(object, self.name):
            self.set_value(getattr(object, self.name))

    def show_default(self):
        self.displayvalue = self.default
        [elem.show_default() for elem in self.elements.values()]
        
    def show_value(self):
        self.displayvalue = self.value
        [elem.show_value() for elem in self.elements.values()]
        
    def show_request_value(self):
        self.displayvalue = self.request_value
        [elem.show_request_value() for elem in self.elements.values()]
        


class CCFormField(FormField):

    def set_request(self, request, validate = True):
        FormField.set_request(self, request, validate)

        if (
            self.currentvalue and 
            self.isvalid and 
            validate and 
            not self.luhn_mod_ten(self.currentvalue)):
            
            self.isvalid = False
            self.valid_message = 'invalid credit card number'

   
    def luhn_mod_ten(self, ccnumber):
        """ checks to make sure that the card passes a luhn mod-10 checksum.
        
        courtesy: http://aspn.activestate.com
        """

        sum = 0
        num_digits = len(ccnumber)
        oddeven = num_digits & 1

        for count in range(0, num_digits):
            digit = int(ccnumber[count])

            if not (( count & 1 ) ^ oddeven ):
                digit = digit * 2
            if digit > 9:
                digit = digit - 9

            sum = sum + digit

        return ( (sum % 10) == 0 )
    
    
class DateFormField(CompoundFormField):
    def __init__(self, name, fields, yeardeltas = range(-5, 5), required = False, *args, **params):

        elements = {}
        
        for field in fields:
            if field == 'ampm':
                elements[field] = FormField(field, required = required)
            else:
                elements[field] = IntFormField(field, required = required)

        for key in ['year', 'month', 'day']:
            if elements.has_key(key):
                self.hasdate = True
                break
        else:
            self.hasdate = False

        for key in ['hour', 'minute', 'second']:
            if elements.has_key(key):
                self.hastime = True
                break
        else:
            self.hastime = False

            
        assert (self.hasdate or self.hastime)
        
        CompoundFormField.__init__(self, name, elements.values(), **params)

        self.valid_message = ""
        self.required = required
        
        if self.hasdate:
            today = datetime.datetime.today()
            year = today.year
            self.yearrange = [year + i for i in yeardeltas]


    def set_compound_values(self, value):
        if self.hasdate:
            self.elements['year'].set_value(value.year)
            self.elements['month'].set_value(value.month)
            self.elements['day'].set_value(value.day)
            
        if self.hastime:
            if self.elements.has_key('ampm'):
                v = value.hour % 12
                if v == 0: v = 12
                self.elements['hour'].set_value(v)
            else:
                self.elements['hour'].set_value(value.hour)
            self.elements['minute'].set_value(value.minute)
            self.elements['second'].set_value(value.second)
            if self.elements.has_key('ampm'):
                self.elements['ampm'].set_value(value.hour > 12 and 'pm' or 'am')
        
        
    def get_valid_message(self):
        return self.valid_message
        
    def set_request(self, request, validate = True):
        CompoundFormField.set_request(self, request, validate)
        if validate:
            for elem in self.elements.values():
                if elem.is_valid() is False:
                    self.valid_message = 'field "%s": %s' % (self.description, elem.get_valid_message())
                    return

            args = {}

            has_value = False
            if self.hasdate:
                dummy = datetime.date.min
                for key in ['year', 'month', 'day']:
                    if self.elements.has_key(key):
                        args[key] = self.elements[key].currentvalue
                        if args[key] is not None:
                            has_value = True
                    else:
                        args[key] = getattr(dummy, key)
                
            if self.hastime:
                dummy = datetime.time.min
                for key in ['hour', 'minute', 'second']:
                    if self.elements.has_key(key):
                        args[key] = self.elements[key].currentvalue
                        if args[key] is not None:
                            has_value = True
                    else:
                        args[key] = getattr(dummy, key)
                
                if self.elements.has_key('ampm'):
                    if self.elements['ampm'] == 'pm':
                        args['hour'] += 12
                    elif args['hour'] == 12:
                        args['hour'] = 0

            if not has_value:
                self.request_value = None
                return
                
            try:
                if self.hasdate and self.hastime:
                    value = datetime.datetime(**args)
                elif self.hasdate:
                    value = datetime.date(**args)
                else:
                    value = datetime.time(**args)
                self.request_value = value
                self.currentvalue = value
                self.isvalid = True
            except TypeError, e:
                self.isvalid = False
                self.currentvalue = None
                self.valid_message = 'field "%s" does not contain a valid date/time (%s)' % (self.description, str(e))
            except ValueError, e:
                self.isvalid = False
                self.currentvalue = None
                self.valid_message = 'field "%s" does not contain a valid date/time (%s)' % (self.description, str(e))
            
            
