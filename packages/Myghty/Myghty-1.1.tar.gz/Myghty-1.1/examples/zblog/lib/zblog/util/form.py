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

class FormElement(object):
    def __init__(self, name,  **params):
        self.name = name
        self.description = ''
        self.errors = []
        self.isvalid = None
    def set_form(self, form):pass
    def set_request(self, req, validate = True):pass

    def append_error(self, error):
        self.errors.append(error)
        self.isvalid=False
    
    def clear(self):pass
    def is_valid(self):return self.isvalid
    def unvalidate(self):pass
    
class Form(FormElement):
    def __init__(self, name, elements, **params):
        FormElement.__init__(self, name)
        self.success = []
        
        self.elements = OrderedDict()
        for elem in elements:
            self.elements[elem.name] = elem
            elem.set_form(self)

    def append_success(self, success):
        self.success.append(success)

    def set_form(self, form):pass
        
    def append(self, element):
        self.elements[element.name] = element
        element.set_form(self)
        
    def __iter__(self):
        return iter(self.elements.values())

    def get(self, key, *args, **kwargs):
        return self.elements.get(key, *args, **kwargs)
    def __getitem__(self, key):
        return self.elements[key]
    def __setitem__(self, key, elem):
        self.elements[elem.name] = elem
        elem.set_form(self)
        
    def unvalidate(self):
        self.isvalid = None
        for elem in self.elements.values(): elem.unvalidate()
    
    def set_request(self, req, validate = True):
        self.isvalid = True
        for elem in self.elements.values():
            if elem is None:
                continue
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

    def clear(self):
        for elem in self.elements.values():
            elem.clear()
    
class SubForm(Form):
    def _fieldname(self, formfield):
        return self.name + "_" + formfield.name
        
class FormField(FormElement):
    def __init__(self, name, description=None, required=False, default=None, data=None, attribute=False, setattribute=False, getattribute=False, disabled=False):
        FormElement.__init__(self, name)

        if description is None:
            self.description = name
        else:
            self.description = description
        
        self.required = required

        if setattribute is not False:
            self.setattribute = setattribute
        elif attribute is not False:
            self.setattribute = attribute
        else:
            self.setattribute = name
        if getattribute is not False:
            self.getattribute = getattribute
        elif attribute is not False:
            self.getattribute = attribute
        else:
            self.getattribute = name

        self.default = default
        self.value = default
        self.displayname = None
        self.data = data
        self.disabled = disabled
    
    def clear(self):
        self.value = self.default
        
    def set_form(self, form):
        self.displayname = form._fieldname(self)

    def _set_value(self, value):
        self._value = value
        if value is None:
            self.display = ''
        else:
            self.display = str(value)

    value = property(lambda s: s._value, lambda s, v: s._set_value(v))
    
    def reflect_to(self, object):
        if self.disabled or self.setattribute is None:
            return
        elif callable(self.setattribute):
            self.setattribute(self, object)
        else:
            attrs = self.setattribute.split('.')
            o = object
            for attr in attrs[0:-2]:
                o = getattr(o, attr)
            setattr(o, attrs[-1], self.value)

    def reflect_from(self, object):
        if self.getattribute is None:
            return
        elif callable(self.getattribute):
            self.value = self.getattribute(object)
        else:
            for attr in self.getattribute.split('.'):
                try:
                    object = getattr(object, attr)
                except AttributeError:
                    return
            self.value = object

    def set_request(self, request, validate = True):
        """sets the request for this form.   if validate is True, also 
        validates the value."""

        if request.has_key(self.displayname):
            self.display = request[self.displayname]
            
        if validate:
            if self.required and (not request.has_key(self.displayname) or not self.display):
                self.isvalid = False
                self.append_error('required field "%s" missing' % self.description)
            else:
                self.isvalid = True
                self.value = self.display
                
    def unvalidate(self):
        """resets the isvalid state of this form to None"""
        self.isvalid = None
        self.errors = []
        

class IntFormField(FormField):

    def _set_value(self, value):
        if not value:
            self._value = None
            self.display = ''
        else:
            try:
                self._value = int(value)
            except ValueError:
                self.append_error('field "%s" must be an integer number' % self.description)
                self.isvalid = False
            self.display = str(value)
            
                
class CompoundFormField(SubForm):
    """
    a SubForm that acts like a single formfield in that it contains a single value,
    but also contains subfields that comprise elements of that value.
    
    examples: a date with year, month, day fields, corresponding to a date object
    
    more exotic examples: a credit card field with ccnumber, ccexpiration fields corresponding to a 
    CreditCard object, an address field with multiple subfields corresopnding to an Address object, etc.
    
    """

    def _set_value(self, value):
        SubForm._set_value(self, value)
        self.set_compound_values(value)        

    def set_compound_values(self, value):
        pass
        


class CCFormField(FormField):

    def _set_value(self, value):
        if not self.luhn_mod_ten(value):
            self.isvalid = False
            self.append_error('invalid credit card number')
        else:
            self._value = value
   
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
    # TODO: fixy
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

        self.required = required
        
        if self.hasdate:
            today = datetime.datetime.today()
            year = today.year
            self.yearrange = [year + i for i in yeardeltas]


    def set_compound_values(self, value):
        if self.hasdate:
            self.elements['year'].value = value.year
            self.elements['month'].value = value.month
            self.elements['day'].value = value.day
            
        if self.hastime:
            if self.elements.has_key('ampm'):
                v = value.hour % 12
                if v == 0: v = 12
                self.elements['hour'].value = v
            else:
                self.elements['hour'].value = value.hour
            self.elements['minute'].value = value.minute
            self.elements['second'].value = value.second
            if self.elements.has_key('ampm'):
                self.elements['ampm'].value = (value.hour > 12 and 'pm' or 'am')
        
    def set_request(self, request, validate = True):
        CompoundFormField.set_request(self, request, validate)
        if validate:
            for elem in self.elements.values():
                if elem.is_valid() is False:
                    self.append_error('field "%s": %s' % (self.description, string.join([elem.errors])))
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
                self.append_error('field "%s" does not contain a valid date/time (%s)' % (self.description, str(e)))
            except ValueError, e:
                self.isvalid = False
                self.currentvalue = None
                self.append_error('field "%s" does not contain a valid date/time (%s)' % (self.description, str(e)))
            
            
