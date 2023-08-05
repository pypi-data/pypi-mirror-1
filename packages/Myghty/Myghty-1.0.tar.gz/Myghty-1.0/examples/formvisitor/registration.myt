<%doc>
  an example firstname/lastname/occupation registration form.
</%doc>

<%python>

import formvisitor as form

registerform = form.Form('myform', 'register.myt', elements = [
	form.TextField('firstname', 'First Name', size=50),
	form.TextField('lastname', 'Last Name', size=50),
	form.SelectField('occupation', 'Occupation', 
	options = [
		form.OptionField('skydiver', 'Sky Diver'),
		form.OptionField('programmer', 'Computer Programmer'),
		form.OptionField('', 'No Answer'),
	]
	),
	form.SubmitField('register')
	]
)
</%python>

<p>
This page illustrates the usage of module components to create programmatically-oriented page components, in contrast to regular template-oriented components.
<ul>
<li><a href="/source/examples/formvisitor/registration.myt">registration.myt</a> - This page, defines the formfields below as a data structure, which is then passed to the FormGenerator method. </li>
<li><a href="/source/examples/formvisitor/formfields.myc">formfields.myc</a> - Defines the HTML implementation of each type of form field.</li>
<li><a href="/source/examples/formvisitor/lib/formvisitor.py">formvisitor.py</a> - Provides the FormGenerator object which traverses a given Form object and invokes the proper methods within formfields.myc via a visitor pattern.</li>
<li><a href="/source/examples/formvisitor/register.myt">register.myt</a> - Target page which displays form post results.</li>
</ul>
</p>

Welcome to the Skydivers or Computer Programmers Club !

<& @formvisitor:generate_form, form = registerform &>


<%method title>
Myghty Examples - Form Visitor
</%method>


