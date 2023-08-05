<span class="headertext1">Myghty Demo Store Architecture</span>

<p>The Myghty Store is laid out in a model-view-controller pattern:</p>

<ul>
	<li><p><a href="<& common.myc:store_uri &>source/lib/shoppingcontroller.py">shoppingcontroller.py</a> - this module contains a class instance that serves as the controller, which is referenced by the module variable 'index'.  Each method of the class is served as a Module Component.  The resolution of URIs to these module components is specified in the Myghty configuration parameter "module_root".  This configuration parameter can be seen in the sample httpd.conf file as well as the example standalone runner run_cart.py.</p>
<p>
An alternative to module_root which is a more specific to individual URL patterns, as well as a little more secure, is module_components, which references URL patterns to specific module component objects.
</p>

	
	<p>shoppingcontroller is responsible for receiving input from the request, pulling data from the data storage module as well as the user's current session, and configuring the proper response template as well as the data used by that template.  All templates that are called by shoppingcontroller are in the <b>templates/</b> folder.</p>
	
	<li><p><a href="<& common.myc:store_uri &>source/lib/shoppingmodel.py">shoppingmodel.py</a> - this module defines a set of classes which formulate the business entities used by the store.  Real-world concepts like items, users, shopping carts, and item categories are laid out as Python classes.</p>
	
	<li><p><a href="<& common.myc:store_uri &>source/lib/shoppingdata.py">shoppingdata.py</a> - this module serves as a micro-database of a store's catalog.  For most ecommerce applications, shoppingdata.py would be a library of database access code which queries a database and formats the resulting data into entity objects, i.e. instances of the classes found in the shoppingmodel module.  For the purpose of this example application, it is merely a hardcoded set of product names and descriptions, organized into categories.
</ul>

<p>The file layout is as follows:</p>
<ul>
	<li><p><b>components/</b> - contains Myghty component files, which are always referenced by another Myghty template as either a straight included component, or as a source of method components.  These files have the extension .myc.  Included here are regular layout components such as the <a href="<& common.myc:store_uri &>source/components/header.myc">header</a>, the <a href="<& common.myc:store_uri &>source/components/sidebar.myc">sidebar</a>, the <a href="<& common.myc:store_uri &>source/components/autohandler">root autohandler</a>, as well as the method
	libraries <a href="<& common.myc:store_uri &>source/components/common.myc">common.myc</a> and <a href="<& common.myc:store_uri &>source/components/forms.myc">forms.myc</a>.</p>
	
	<li><p><b>htdocs/</b> - these are Myghty templates that are served directly, without being supplied arguments by a controller.  While these templates could be served directly from the Myghty handler, in this case the ApacheHandler,
	this particular application's configuration has them served via a controller called a PathTranslator, which strips off
	the leading "<& common.myc:store_uri &>" prefix from the file URI before having Myghty service the template request.</p>
	
	<li><p><b>templates/</b> - these Myghty templates are always serviced from a module component first (i.e. a controller), and all of them require arguments to be set up by its controller.</p>
	
	<li><p><b>lib/</b> - this is where the regular Python modules are located.  A sample httpd.conf file is here as well.</p>
</ul>

