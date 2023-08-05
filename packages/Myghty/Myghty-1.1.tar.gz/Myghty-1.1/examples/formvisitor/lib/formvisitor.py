import myghty.component as component


# the generate_form module component          
def generate_form(m, form):          
    form.accept_visitor(RenderForm(m))


# base class for an element in an HTML form
class FormElement(object):
    def __init__(self):
        pass

    def accept_visitor(self, visitor): 
        pass

# FormElement implementations
class Form(FormElement):

    def __init__(self, name, action, elements):
        self.name = name
        self.action = action
        self.elements = elements

    def accept_visitor(self, visitor):
        visitor.visit_form(self)

class Field(FormElement):

    def __init__(self, name, description, value = None):
        self.name = name
        self.description = description
        self.value = value

class TextField(Field):

    def __init__(self, name, description, size, value = None):
        Field.__init__(self, name, description, value)
        self.size = size

    def accept_visitor(self, visitor):
        visitor.visit_textfield(self)

class SelectField(Field):

    def __init__(self, name, description, options, value = None):
        Field.__init__(self, name, description, value)
        self.options = options
        for o in self.options:
            o.parent = self
            if o.id == self.value:
                o.selected = True

    def accept_visitor(self, visitor):
        visitor.visit_selectfield(self)

class OptionField(FormElement):
    """an <OPTION></OPTION> tag.  contains a parent attribute that points to a <SELECT> field."""

    def __init__(self, id, description):
        self.id = id
        self.description = description
        self.parent = None
        self.selected = False

    def accept_visitor(self, visitor):
        visitor.visit_option(self)

class SubmitField(FormElement):
    """an <INPUT TYPE="submit"> field."""

    def __init__(self, value):
        self.value = value

    def accept_visitor(self, visitor):
        visitor.visit_submit(self)


# defines an interface for an object that can be 
# walked along a FormElement structure
class FormVisitor:
          def visit_form(self, form):pass
          def visit_textfield(self, textfield):pass
          def visit_selectfield(self, selectfield):pass
          def visit_option(self, option):pass
          def visit_submit(self, submit):pass
          
          
          
# subclass of FormVisitor that walks along a FormElement
# structure and renders components in a request output stream
class RenderForm(FormVisitor):
      def __init__(self, m):
              self.m = m

      def visit_form(self, form):
              def formcontent():
                      for element in form.elements:
                              element.accept_visitor(self)

              self.m.execute_component("/examples/formvisitor/formfields.myc:form", args = dict(form = form), content=formcontent)

      def visit_textfield(self, textfield):
              self.m.comp("/examples/formvisitor/formfields.myc:textfield", textfield = textfield)

      def visit_selectfield(self, selectfield):
              def selectcontent():
                      for element in selectfield.options:
                              element.accept_visitor(self)

              self.m.execute_component("/examples/formvisitor/formfields.myc:select", args = dict(select = selectfield), content=selectcontent)

      def visit_option(self, option):
              self.m.comp("/examples/formvisitor/formfields.myc:option", option = option)

      def visit_submit(self, submit):
              self.m.comp("/examples/formvisitor/formfields.myc:submit", submit = submit)