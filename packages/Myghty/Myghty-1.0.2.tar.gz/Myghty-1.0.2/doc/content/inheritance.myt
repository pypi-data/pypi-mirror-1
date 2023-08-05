<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="inheritance", description="Inheritance", &>
<p>Inheritance allows a file-based component to be "wrapped" by another file-based component.   This means the requested page executes as a method call inside of the inheriting page, which executes first.  
The basic idea of this is to allow a whole set of pages to have standardized behavior applied to them by an "inheriting" component, the application of which can be as simple as a standard header and footer, or something more complicated such as an authentication scheme, a content caching scheme, or a filtering scheme.
</p>
<p>Inheritance also establishes a relationship between pages with regards to method calling as well as component attributes.  </p>

<&|doclib.myt:item, name="wrapper", description="The Wrapper Chain", &>
<p>A set of pages that all inherit each other is sometimes called the "wrapper chain".  The wrapper chain is an actual property of the request, and is determined dynamically for each new request based on what files are present in the filesystem and what inheritance pattern they specify.  When a template X inherits from a template Y, and that template in turn inherits from template Z, the wrapper chain is created:
</p>

<&|formatting.myt:code&>
	Z -> Y -> X
</&>

<P>The request above was called specifying component X as the requested component.  X inherits from Y, either via an explicit flag or an autohandler configuration (more on that later), and Y inherits from Z.  Therefore a wrapper chain with Z at the beginning and X at the end is created.  
When the request executes, control is passed to Z first.  Z performs its component operations, then programmatically instructs the request to call the next component in the wrapper chain, which is Y.  Y does the same thing and calls X, the originally requested component.  When X is complete, control passes back to Y, and when Y is complete, control passes back to Z.</p>

<p>The flag used to specify that a component should inherit from another is called "inherit", and is specified in the <% "<%flags>" %> section of the component.  The component to inherit from is specified by its component-root-relative URI.  When an inherited parent component wants to call its inheriting child, it usually uses the <&formatting.myt:link, path="request_methods", method="call_next"&> method of the request object.  The child is only executed if its inherited parent explicitly does so.
</p>

<p>If no "inherit" flag is specified for a page, the page will attempt to inherit from a template in the nearest enclosing directory named "autohandler".  Whereas the inherit flag allows a component to explicitly specify its inherited parent, the autohandler mechanism allows the configuration of implicitly inheriting parents.  Autohandlers are described in the next section <&formatting.myt:link, path="specialtempl_autohandler", text="Autohandlers"&>.</p>

</&>

<&|doclib.myt:item, name="example", description="Example - Basic Wrapping", &>


<p>In this example, the requested page is called "index.myt", and its inherited parent is called "base.myt".  base.myt supplies a standard HTML header and footer, and index.myt supplies the content in the middle of the <% "<body>" | h %> tags.</p>



	<&|formatting.myt:code, title="index.myt, inherits from base.myt"&><%text>
	<%flags>inherit='/base.myt'</%flags>


	I am index.myt
	</%text></&>


	<&|formatting.myt:code, title="base.myt, the parent template"&><%text>
	<html>
	<body>

	<h3>example of content wrapping</h3>

	# fetch the next component in the wrapper chain
	# and call it
	% m.call_next()

	</body>
	</html>
	</%text></&>

	The resulting document would be:
	<&|formatting.myt:code&><%text>
	<html>
	<body>

	<h3>example of content wrapping</h3>
	
	I am index.myt
	
	</body>
	</html>
	</%text></&>

<p>While the <&formatting.myt:link, path="request_methods", method="call_next"&> method of request is the simplest way to call the next component in the wrapper chain, the method <&formatting.myt:link, path="request_methods", method="fetch_next"&> exists to pop the next component off the chain but not execute it, as well as <&formatting.myt:link, path="request_methods", method="fetch_all"&> which pops off and returns the entire list of components in the wrapper chain.
</p>

</&>




<&|doclib.myt:item, name="basecomp", description="The Base Component", &>
<p>In the wrapper chain <% '"Z -> Y -> X"' | h%> described at the beginning of the section, the component X is known as the request component, and is accessible throughout the life of the request via the <&formatting.myt:link,path="request_members", member="request_component"&> member of the request.  It also is established as the initial "base component" of the request.  The base component is accessible via the <&formatting.myt:link,path="request_members", member="base_component"&> request member, and it is defined first as the lead requested component in a wrapper chain.  When methods in other template files are called, the base component changes to be the file that the method appears in, throughout the life of that method's execution, and upon method completion returns to its previous value.</p>

<p>The base component is also referred to by the special component keyword 'SELF'.   This keyword can be used directly via the <&formatting.myt:link, path="request_methods", method="fetch_component"&> method, but it is more commonly referenced in method component calls, as detailed in the next section.
</&>

<&|doclib.myt:item, name="method", description="Method and Attribute Inheritance", &>
<p>Methods, first described in <&formatting.myt:link, path="components_methods" &>, are normally called with the <% "<location>:<methodname>"|h%> syntax, where <% "<location>"|h%> is the URI or special keyword identifier of a component, and <% "<methodname>"|h%> is the name of the method to search for.
This syntax enables the component to search not only its local method list for the requested method, it also will search its immediate parent for the method if not found, and that parent will continue the search up the wrapper chain.
</p>

<p>
It is for this reason that the base component and the SELF keyword is of particular value in fetch_component and method calls, since it indicates the innermost component in the current inheritance chain.  An template at the end of a wrapper chain (i.e. template Z in the previous section) can specify the SELF keyword when calling a method, and the method will be located from the innermost template first (i.e. component X), and on up the wrapper chain until found.
</p>

<p>Similarly, component attributes are located using an inheritance scheme as well.  Attributes are referenced via the <&formatting.myt:link, path="components_members", member="attributes"&> member of the component object.  The attributes dictionary, while it is a regular dictionary interface, will search for requested values in the parent of the component if not found locally.
</p>

</&>

<&|doclib.myt:item, name="methodexample", description="Method Inheritance Example", &>
<P>Here is an example where the parent component is an autohandler, which because of its name, automatically becomes the inherited parent of the child component, as long as the child component does not explicitly specify otherwise.</p>

<p>Both in the parent component as well as the child component that inherits from it specify a method "title".  The autohandler can render the title of the page via the "title" method, where it is guaranteed to exist at least in the autohandler's own version of the method, but can be overridden by the inheriting page.  Additionally, the autohandler has an <% "<%attr>" %> section indicating the path to a file location.  The child page will look in its own attribute dictionary for this location, where it will ultimately come from the inheriting parent.</p>

	<&|formatting.myt:code, title="autohandler - specifies root title method and attributes"&><%text>
		<%attr>
			# path to some files
			fileroot = '/docs/myfiles'
		</%attr>
		
		<html>
		<head>
			<title>
		# 	the "title" method is called here from SELF,
		#	so the method will be searched in the base component first,
		# 	then traverse up the inheritance chain until found
			<& SELF:title &>
			</title>
		</head>
		<body>
		
		# call the next component in the wrapper chain
		% m.call_next()
		
		</body>
		</html>

		# default "title" method implementation
		<%method title>
		Welcome to My Site
		</%method>
		
	</%text></&>	

	<&|formatting.myt:code, title="pressrelease.myt - overrides title method"&><%text>
		<%python scope="init">
			# locate the file root via a parent attribute
			pr = get_press_releases(fileroot = self.attributes['fileroot'])
		</%python>

		# specify a title method to override that of the parent's
		<%method title>
		My Site: Press Releases
		</%method>

		<h2>Press Releases</h2>
		
		% for release in pr:
		
		#    ... print data ...
		
		%
		
	</%text></&>	


	

	</&>

</&>


