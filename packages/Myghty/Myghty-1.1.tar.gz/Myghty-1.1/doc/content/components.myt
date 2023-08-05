<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="components", description="Components", &>
	<p>All templates in Myghty are referred to as "Components".  Components, while they may look like plain HTML pages with a few lines of Python in them,  are actually callable units of code which have their own properties, attributes, input arguments, and return values.  One can think of a Component anywhere within the spectrum between "HTML page" and "callable Python object", and use it in either way or a combination of both.</p>
	
	<p>A single template, while it is a component itself, also can contain other components within it, which are referred to as "subcomponents", and a subcategory of subcomponents called "methods".  The template's component itself is called a "file-based component", and when it is the main component referenced by a request it is also known as the "top level component".</p>
	
	<p>When a component is instantiated within the runtime environment, it is a Python object with the usual reference to "self" as well as its own attributes and methods, and the body of the component occurs within a function call on that object.  All components extend from the base class <span class="codeline">myghty.component.Component</span>.  File-based components extend from <span class="codeline">myghty.component.FileComponent</span> and subcomponents extend from <span class="codeline">myghty.component.SubComponent</span>.
	
	<p>Additionally, unique to Myghty is a non-template form of component called a "module component", which is written instead as a regular Python class.  These components are described in the next section, <&formatting.myt:link,path="modulecomponents"&>, extending from the class <span class="codeline">myghty.component.ModuleComponent</span>.</p>
	
	<&|doclib.myt:item, name="example", description="Component Calling Example", &>
	<p>The most basic component operation is to have one template call another.  In the simplest sense, this is just an HTML include, like a server side include.  To have a template "page.myt" call upon another template "header.myt":</p>
	
	<&|formatting.myt:code, title="page.myt"&><%text>
		<html>
			<& header.myt &>
			<body>
			... rest of page
			</body>
		</html>
	</%text></&>
	
	<&|formatting.myt:code, title="header.myt"&><%text>
		<head>
			<title>header</title>
		</head>
	</%text></&>

	<p>Produces:</p>

	<&|formatting.myt:code, syntaxtype="html"&><%text>
		<html>
		<head>
			<title>header</title>
		</head>
			<body>
			... rest of page
			</body>
		</html>
	</%text></&>
	
	</&>
	
	<&|doclib.myt:item, name="pathscheme", description="Component Path Scheme", &>
	<p>
	When calling components, the path to the component is given as an environment-specific URI, and not an actual filesystem path.  While the path can be specified as absolute, it is still determined as relative to one or more of the configured Myghty component roots.  Myghty uses the <&formatting.myt:link, path="parameters", param="component_root"&> parameter as a list of filesystem paths with which to search for the requested component.   If a relative path is used, the path is converted to an absolute path based on its relation to the location of the calling component, and then matched up against the list of component roots.
	</p>
		
	
	</&>	
	
	<&|doclib.myt:item, name="args", description="Component Arguments - the &lt;%args&gt; tag", &>
	<p>Components, since they are really Python functions, support argument lists.  These arguments are supplied to the top-level component from the client request arguments, such as via a POST'ed form.   When a component is called from another component, the calling component specifies its own local argument list to be sent to the called component.</p>
	
	<p>A component can access all arguments that were sent to it by locating them in the ARGS dictionary.  More commonly, it can specify a list of arguments it would like to receive as local variables via the <% "<%args>" %> tag:</p>
	
	<&|formatting.myt:code&><%text>
		<%args>
			username
			password
			
			# sessionid defaults to None
			sessionid = None
		</%args>
		<%python scope="init">
			if sessionid is None:
				sessionid = create_sid()
				
			if password != get_password(username):
				m.send_redirect("loginfailed.myt", hard=True)
		</%python>	
		
	</%text></&>
	
	<p>In the above example, the 'username' and 'password' arguments are required; if they are not present in the argument list sent to this component, an error will be raised.  The 'sessionid' argument is given a default value, so it is not required in the argument list.</p>

	<P>A component like the one above may be called with a URL such as:</p>
	<&|formatting.myt:code, syntaxtype=None&><%text>
		http://foo.bar.com/login.myt?username=john&password=foo&sessionid=57347438
	</%text></&>
	
	<p>The values sent in an <% "<%args>" %> section are analgous to a Python function being called with named parameters.  The above set of arguments, expressed as a Python function, looks like this:</p>
	<&|formatting.myt:code, syntaxtype="python"&><%text>
		def do_run_component(self, username, password, sessionid = None):
	</%text></&>
	<p>What this implies is that the default value sent for "sessionid" only takes effect within the body of the component.  It does <b>not</b> set a default value for "sessionid" anywhere else.  Different components could easily set different default values for "sessionid" and they would all take effect if "sessionid" is not present in the argument list.</p>
	
	
	<p>Components can pass argument lists to other components when called.  Below, a component 'showuser.myt' is called by another component 'page.myt':</p>
	
	<&|formatting.myt:code, title="showuser.myt"&><%text>
		<%args>
			username
			email
		</%args>
		
		Username: <% username %><br/>
		Email: <a href="mailto:<% email %>"><% email %></a><br/>
	</%text></&>

	<&|formatting.myt:code, title="page.myt"&><%text>
		Login information:
		<& showuser.myt, username='john', email='jsmith@foo.com' &>
	</%text></&>

	<p>The component call tags "<% '<& &>' %>" take a named-parameter list just like a Python function, and can also have as the very last argument dictionary with ** notation just like in regular Python:</p>
	
	<&|formatting.myt:code&><%text>
		<& comp.myt, arg1=3.7, **ARGS &>
	</%text></&>
	
	<p>Above, the dictionary ARGS always has a list of all arguments sent to the component, regardless of whether or not they were specified in the <% "<%args>" %> section.   This is a way of passing through "anonymous" arguments from a component's caller to its components being called.</p>
	
	
	<&|doclib.myt:item, name="argscope", description="Argument Scope: component/request/subrequest/dynamic", &>
	<p>So far we have talked about "component-scoped" arguments, that is, the list of arguments that are sent directly to a component by its caller.  While the very first component called in a request (i.e. the top-level component) will receive the client request arguments as its component-scoped arguments, any further component  calls will only receive the arguments sent by its direct caller.</p>
	
	<p>To make it easier for all components to see the original request arguments, the attribute <span class="codeline">scope="request"</span> may be specified in any <% "<%args>" %> section to indicate that arguments should be taken from the original request, and not the immediate caller.  Normally, the default value of <span class="codeline">scope</span> is <span class="codeline">component</span>, indicating that only the immediate component arguments should be used.</p>

	<&|formatting.myt:code&><%text>
		<%args scope="request">
			sessionid
		</%args>
		
		<%args scope="component">
			username
		</%args>
		
		hello <% username %>, to edit your preferences click
		<a href="prefs.myt?sessionid=<% sessionid %>">here</a>.
		
	</%text></&>

	<p>Above, the argument "sessionid" must be sent by client request, but the argument "username" must be sent by the calling component.  If this component is called as the top-level component, both arguments must be present in the client request.</p>
	
	<p>
	Request arguments are also always available via the <&formatting.myt:link, path="request_members", member="request_args"&> and <&formatting.myt:link, path="request_members", member="root_request_args"&> members of the request object.
	</p>

	<p>Note that there is special behavior associated with request-scoped arguments when using subrequests (described later in this section).  Since a subrequest is a "request within a request", it is not clear whether the "request" arguments should come from the originating request, or the immediate, "child" request.  The attribute <span class="codeline">scope="subrequest"</span> indicates that arguments should be located in the immediate request, whether or not it is a subrequest, in contrast to <span class="codeline">scope="request"</span> which always refers to the arguments of the ultimate root request.  Subrequests are described in the section  <&formatting.myt:link, path="components_programmatic_subrequests"&> below.
	</p>

    <p>
    The component that wants to be flexible about its arguments may also specify its arguments with "dynamic" scope.  In dynamic scope, the argument is located within the most local arguments first, and then upwards towards the request until found.  The following component will retrieve its arguments locally if present, or if not, from the request, no matter where it is called:
    </p>

    <&|formatting.myt:code&><%text>
    	<%args scope="dynamic">
    		username
    		email
    	</%args>

    	hello <% username %>, your email address is <% email %>.

    </%text></&>

	</&>
	
	

	</&>
	
	<&|doclib.myt:item, name="subcomponent", description="How to Define a Subcomponent", &>
	<p>A subcomponent is a component defined within a larger template, and acts as a callable "subsection" of that page.  Subcomponents support almost all the functionality of a file-based component, allowing Python blocks of init, cleanup and component scope, but not global, request or thread scope.</p>  
	
	
	<p>A subcomponent, albeit a nonsensical one, looks like this:</p>
	
	<&|formatting.myt:code&><%text>
	<%def mycomponent>
		<%args>
			arg1 = 'foo'
			arg2 = 'bar'
		</%args>
		<%python scope="init">
			string = arg1 + " " + arg2
		</%python>
		
		i am mycomponent !
		
		<% string %>
	</%def>
	</%text></&>
	<p>A regular subcomponent like this one is always called by another component, i.e. it can never be called directly from the request as a top-level component.  Furthermore, subcomponents defined with the <span class="codeline"><% "<%def>" %></span> tag are private to the template file they appear in.</p>
	
	<p>The subcomponent has access to all global variables, such as <i>m</i> and <i>r</i>, but it does not have access to the local variables of its containing component.  This would include variables specified in the body of the main component, i.e. in init-, cleanup- and component-scoped <% "<%python>" %> blocks.  Variables declared in global-, request- and thread-scoped <% "<%python>" %> blocks are available within subcomponents, subject to the restrictions on variables declared in those blocks.  Variables declared within the body of a subcomponent remain local to that subcomponent.</p>
	
	<&|doclib.myt:item, name="calling", description="Calling a Subcomponent", &>
	<p>Subcomponents are called in a similar manner as a file-based component:</p>
	
	<&|formatting.myt:code&><%text>
	welcome to <& title, username='john' &>
	
	<%def title>
		<%args>
			username
		</%args>
		
		<b>bling bling bling <% username %> bling bling bling</b
	</%def>
	</%text></&>	

	<p>Note that a subcomponent can be defined at any point in a template and is still available throughout the entire template.</p>
	</&>
	
	</&>
	
	
	<&|doclib.myt:item, name="method", description="How to Define a Method", &>
	<p>A method is similar to a subcomponent, except its functionality is available outside of the file it appears in, and it can take advantage of inheritance from other template files.  </p>
	
	<&|formatting.myt:code&><%text>
	<%method imamethod>
		<%args>
			radius
			coeffiecient = .5424
		</%args>
		<%python scope="init">
			foob = call_my_func(radius, coefficient)
		</%python>

		fractional fizzywhatsle: <% foob %>
	</%method>
	</%text></&>

    
	<&|doclib.myt:item, name="calling", description="Calling a Method", &>
	<p>A method can be called from within the file it appears in the same fashion as a subcomponent, i.e. simply by its name, in which case it is located in the same way as a subcomponent.   The other format of method calling is <%  "<location>:<methodname>" | h%>, where <i>location</i> specifies what component to initially search for the method in.   The location may be specified as the URI of the desired component file, or one of the special keywords SELF, REQUEST, or PARENT.</p>

	<&|formatting.myt:code&><%text>
	# call the method print_date in 
	# component file /lib/functions.myt
	<& /lib/functions.myt:print_date, date="3/12/2004" &>

	# call a method in the local template
	<& tablerow, content="cell content" &>

	# call a method in the base component, taking 
	# advantage of inheritance
	<& SELF:printtitle &>

	</%text></&>	

	
	<p>
	With the compound method calling format, if the method is not located in the specified component, the component's inherited parent will be searched, and in turn that component's inherited parent, etc., until no more parents exist.  The parent-child relationship of components, as well as the keywords SELF, REQUEST, and PARENT are described in the section <&formatting.myt:link, path="inheritance"&>.</p>


	</&>
	
	</&>

		<&|doclib.myt:item, name="closure", description="How to Define a Closure", &>
		Version 0.98 introduces a lightweight alternative to %def and %method called <span class="codeline"><% "<%closure>" %></span>.  This tag defines a local function definition using Python keyword <span class="codeline">def</span>, which is callable via the same mechanism as that of subcomponents.  A closure is in fact not a component at all and can only be used within the block that it is defined, and also must be defined before it is called.  It offers the advantage that it is created within the scope of the current code body, and therefore has access to the same variable namespace:

	<&|formatting.myt:code&><%text>
	<%closure format_x>
	    <%args>
	        format = '%d'
	    </%args>
	    <% format % x %>
	</%closure>

	%   for x in (1,2,3):
	        <& format_x, format='X:%d' &>
	%
	</%text></&>

	<p>Closures support the <% "<%args>" | h%> tag, as well as <&formatting.myt:link, path="scopedpython_init" &> and <& formatting.myt:link, path="scopedpython_cleanup" &>.  Closures can also be nested.  They currently do not support the "component call with content" calling style but this may be added in the future.</p>

	    </&>


	<&|doclib.myt:item, name="flags", description="Subcomponent Flags", &>
	<p>Subcomponents and methods also may specify flags as described in the section <&formatting.myt:link, path="otherblocks_flags"&>.  The most useful flags for a subcomponent are the <&|formatting.myt:codeline&>trim</&> and <&|formatting.myt:codeline&>autoflush</&> flags, described in <&formatting.myt:link, path="filtering"&>.</p>
	
	<p>There are two formats for specifing flags in a subcomponent:</p>
	<&|formatting.myt:code&><%text>
	
	# traditional way
	
	<%def buffered>
		<%flags>
			autoflush=False
		</%flags>
		this is a buffered component
	</%def>
	
	
	# inline-attribute way
	
	<%method hyperlink trim="both">
		<%args>
			link
			name
		</%args>
		
		<a href="<% link %>">name</a>
	</%method>
	
	</%text></&>

	</&>

	<&|doclib.myt:item, name="callwithcontent", description="Component Calls with Content", &>
	<p>Subcomponents and methods can also be called with a slightly different syntax, in a way that allows the calling component to specify a contained section of content to be made available to the called component as a Python function.  Any subcomponent can query the global <i>m</i> object for a function that executes this content, if it is present.  When the function is called, the code sent within the body of the component call with content is executed; this contained code executes within the context and namespace of the calling component.</p>
	
	<&|formatting.myt:code&><%text>
	<&| printme &>
		i am content that will be grabbed by PRINTME.
	</&>
	</%text></&>
	<P>The called component can then reference the contained content like this:</p>
	<&|formatting.myt:code&><%text>
	<%def printme>
		I am PRINTME, what do you have to say ?<br/>
		<% m.content() %>
	</%def>
	</%text></&>
	<p>The method <&|formatting.myt:codeline&>m.content()</&> executes the code contained within the <% "<&| &>/</&> " | h%> tags in its call to "printme", and returns it as a string.  A component may query the request object <i>m</i> for the presense of this function via the method <&|formatting.myt:codeline&>m.has_content()</&>.</p>
	
	<p>A component call with content is one of the most powerful features of Myghty, allowing the creation of custom tags that can produce conditional sections, iterated sections, content-grabbing, and many other features.  It is similar but not quite the same as the template inheritance methodology, in that it allows the body of a component to be distilled into a callable function passed to an enclosing component, but it involves a client explicitly opting to wrap part of itself in the body of another component call, rather than a client implicitly opting to wrap its entire self in the body of another component call.  
	</p>
	
	</&>
	<&|doclib.myt:item, name="programmatic", description="Calling Components Programmatically", &>
		<p>The special component calling tags described above are just one way to call components.  They can also be called directly off of the request object <i>m</i>, which is handy both for calling components within %python blocks as well as for capturing either the return value or the resulting content of a subcomponent.  Component objects can also be directly referenced and executed via these methods.
		</p>
		<p>The full index of request methods and members can be found in <&formatting.myt:link, path="request" &>.</p>
		
		<&|doclib.myt:item, name="comp", description="m.comp(component, **params)", &>
		<p>This method allows you to call a component just like in the regular way except via Python code. The arguments are specified in the same way to the function's argument list.  The output will be streamed to the component's output stream just like any other content.  If the component specifies a return value, it will be returned.  A component, since it is really just a python function, can have a return value simply by using the python statement <&|formatting.myt:codeline&>return</&>.  The value of <i>component</i> can be an actual component object obtained via <&|formatting.myt:codeline&>fetch_component()</&>, or a string specifying a filesystem path or local subcomponent or method location.</p>
		
		<&|formatting.myt:code&><%text>
			<%python>
			m.comp('/foo/bar.myt', arg1='hi')
			</%python>
		</%text></&>
		
		
		</&>
		<&|doclib.myt:item, name="scomp", description="m.scomp(component, **params)", &>
		<p>This method is the same as "comp" except the output of the component is captured in a separate buffer and returned as the return value of scomp().</p>

		<&|formatting.myt:code&><%text>
			<%python>
			component = m.fetch_component('mycomponent')
			content = m.scomp(component)
			
			m.write("<pre>" + content + "</pre>")
			</%python>
		</%text></&>


		</&>
		<&|doclib.myt:item, name="subrequests", description="Subrequests", &>
		<p>
		A subrequest is an additional twist on calling a component, it calls the component with its own request object that is created from the current request.  A subrequest is similar to an internal redirect which returns control back to the calling page.  The subrequest has its own local argument list as well, separate from the original request arguments.
		</p>
		<&|formatting.myt:code&><%text>
			<%python>
				ret = m.subexec('/my/new/component.myt', arg1='hi')
			</%python>
		</%text></&>
		<p>The <span class="codeline">subexec</span> method takes either a string URI or a component object as its first argument, and
		the rest of the named parameters are sent as arguments to the component.</p>
		
		<p>Use subrequests to call a component when you want its full inheritance chain, i.e. its autohandlers, to be called as well.</p>
		
		<p>The <span class="codeline">subexec</span> method is comprised of several more fine-grained methods as illustrated in this example:</p>
		<&|formatting.myt:code&><%text>
			<%python>
				# get a component to call
				component = m.fetch_component('mysubreq.myt')
				
				# make_subrequest - 
				# first argument is the component or component URI,
				# following arguments are component arguments
				subreq = m.make_subrequest(component, arg1 = 'foo')
				
				# execute the request.  return value is sent
				ret = subreq.execute()
			</%python>
		</%text></&>

		<p>The make_subrequest method can also be called as create_subrequest, which in addition
		to supporting component arguments, lets you specify all other request object arguments as well:
		
		<&|formatting.myt:code&><%text>
			<%python>
				import StringIO
				
				# get a component to call
				component = m.fetch_component('mysubreq.myt')

				# make a subrequest with our own 
				# output buffer specified				
				buf = StringIO.StringIO()
				subreq = m.create_subrequest(component, 
					out_buffer = buf,
					request_args = {'arg1':'foo'},
					)
				
				# execute the request.  
				# return value is sent, our own buffer
				# is populated with the component's 
				# content output
				ret = subreq.execute()
				
				
			</%python>
		</%text></&>

		
		</&>

		<&|doclib.myt:item, name="callself", description="call_self(buffer, retval)", &>
		<p>
		The "call_self" method is provided so that a component may call itself and receive its own content in a buffer as well as its return value.  "call_self" is an exotic way of having a component filter its own results, and is also the underlying method by which component caching operates.  Note that for normal filtering of a component's results, Myghty provides a full set of methods described in the section <&formatting.myt:link, path="filtering_filtering"&>, so call_self should not generally be needed.
		</p>
		<p>call_self uses a "reentrant" methodology, like this:</p>
		<&|formatting.myt:code&><%text>
			<%python scope="init">
				import StringIO
				
				# value object to store the return value
				ret = Value()
				
				# buffer to store the component output
				buffer = StringIO.StringIO()
				
				if m.call_self(buffer, ret):
					m.write("woop! call self !" + 
						buffer.getvalue() + " and we're done")
					return ret()
					
				# ... rest of component
			</%python>
		</%text></&>
		<p>The initial call to call_self will return True, indicating that the component has been called and its output and return value captured, at which point the component should return.  Within the call_self call, the component is executed again; call_self returns False to indicate that the thread of execution is "inside" of the initial call_self and that content is being captured.</p>
		<p>It is recommended that call_self be called only in an init-scoped Python block before any other content has been written, else that content will be printed to the output as well as captured.</p>
		</&>

	</&>
	
	<&|doclib.myt:item, name="methods", description="Component Methods", &>
	<p>
	Instances of Component objects can be accessed many ways from the request object, including the  <&formatting.myt:link, path="request_methods", method="fetch_component"&> method, and the 
	<&formatting.myt:link, path="request_members", method="current_component"&>,
	<&formatting.myt:link, path="request_members", method="request_component"&>, and
	<&formatting.myt:link, path="request_members", method="base_component"&> members.  The <&formatting.myt:link, path="request_methods", method="fetch_next"&> method returns the next component in an inheritance chain.  Finally, <&|formatting.myt:codeline&>self</&> refers to the current component.
	</p>

	<P>The methods available directly from <&|formatting.myt:codeline&>Component</&> are listed below, followed by the members.
</p>

	<&|formatting.myt:paramtable&>
		<&|formatting.myt:function_doc, name="call_method", arglist=['methodname', '**params']&>
		<p>Calls a method on the current component, and returns its return value.  This method is shorthand for locating the current request via <&|formatting.myt:codeline&>request.instance()</&>, locating the method via <&|formatting.myt:codeline&>locate_inherited_method()</&> and calling <&|formatting.myt:codeline&>m.comp()</&>.</p>
		</&>

		<&|formatting.myt:function_doc, name="get_flag", arglist=["key", "inherit=False"]&>
		<p>Returns the value of a flag for this component.  If "inherit" is True, the value of the flag will be searched for in the chain of parent components, if it is not found locally.</p>
		</&>

		<&|formatting.myt:function_doc, name="get_sub_component", arglist=['name']&>
		<p>
		Returns the subcomponent denoted by <i>name</i>.  For a subcomponent or method, returns the subcomponent of the owning (file-based) component.  Note this is not for methods; for those, use locate_inherited_method.
		</p>
		</&>
		
		<&|formatting.myt:function_doc, name="has_filter", arglist=[]&>
		<p>
		Returns true if this component has a filter section, and or a "trim" flag.
		</p>
		</&>
		<&|formatting.myt:function_doc, name="locate_inherited_method", arglist=['name']&>
		<p>Returns the method component associated with <i>name</i>.  The method is searched for in the current component and up the inheritance chain.  For a subcomponent or method, returns the method of the owning (file-based) component.  Note this is not for non-method subcomponents; for those, use get_sub_component().
		</&>
		<&|formatting.myt:function_doc, name="scall_method", arglist=['methodname', '**params']&>
		<p>Calls a method on the current component, captures its content and returns its content as a string.  This method is shorthand for locating the current request via <&|formatting.myt:codeline&>request.instance()</&>, locating the method via <&|formatting.myt:codeline&>locate_inherited_method()</&> and calling <&|formatting.myt:codeline&>m.scomp()</&>.</p>
		</&>
		<&|formatting.myt:function_doc, name="use_auto_flush", arglist=[]&>
		<p>
		Returns True or False if this component requires autoflush be turned on or off for its execution, or returns None if no requirement is set.  This method searches within the current components flags, or within parent component flags if not present.
		</p>
		</&>
		
	</&> 
		</&>
		
	<&|doclib.myt:item, name="members", description="Component Members", &>


	<&|formatting.myt:paramtable&>
		<&|formatting.myt:member_doc, name="args"&>
		A list of argument names, corresponding to variable names in the component-scoped <% "<%args>" %> section, which have a default value specified.  
		</&>

		<&|formatting.myt:member_doc, name="attr"&>
		A dictionary of component attributes, corresponding to those set by the <% "<%attr>" %> tag.  The attributes can be set at once
		by assigning a dictionary to this member.  However, to set and retrieve individual attributes, it is best to use the special <&formatting.myt:link, member="attributes"&> member which takes advantage of inheritance.
		</&>

		<&|formatting.myt:member_doc, name="attributes"&>
		A dictionary accessor for the <&formatting.myt:link, member="attr"&> dictionary member that locates its members first in the local component attributes, then searches up the inheritance chain for the attribute.
		</&>
		
		<&|formatting.myt:member_doc, name="dir_name"&>
		<p>The web-specific directory name where the current component resides, i.e. for this component its "<% self.dir_name %>".  For a subcomponent or method, it is the directory name of the owning (file-based) component.</p>
		</&>

		<&|formatting.myt:member_doc, name="file"&>
		<p>The actual filesystem location of a component, for a component that was loaded directly from a Myghty template file, else it is <span class="codeline">None</span>.</p>
		</&>

		<&|formatting.myt:member_doc, name="filter"&>
		<p>Reference to the function that will perform filtering on the component.  This filter is directly stated in the <% "<%filter>" %> section described in <&formatting.myt:link, path="filtering_filtering_filter"&>.</p>
		</&>

		<&|formatting.myt:member_doc, name="flags"&>
		Dictionary of flags for this component.  Also can be accessed via the <&formatting.myt:link, path="components_programmatic_methods", method="get_flag"&> method.
		</&>
		
		<&|formatting.myt:member_doc, name="id" &><p>A unique identifier for the current component, which is comprised of the key name for its component root joined with its web-specific path, i.e. for this component its "<% self.id %>".
		</&>

		<&|formatting.myt:member_doc, name="is_file_component", arglist=[]&>
		<p>True if this component is a file based component.</p>
		</&>
		<&|formatting.myt:member_doc, name="is_method_component", arglist=[]&>
		<p>True if this component is a method component.</p>
		</&>
		<&|formatting.myt:member_doc, name="is_module_component", arglist=[]&>
		<p>True if this component is a module component.</p>
		</&>
		<&|formatting.myt:member_doc, name="is_sub_component", arglist=[]&>
		<p>True if this component is a subcomponent or method component.</p>
		</&>

		<&|formatting.myt:member_doc, name="name", &>
		<p>The filename or name of the current component, i.e. for this component its "<% self.name %>".
		</&>
		
		<&|formatting.myt:member_doc, name="owner"&>
		<p>For a subcomponent or method subcomponent, the owning file-based component, otherwise it is self.</p>
		</&>
		
		<&|formatting.myt:member_doc, name="parent_component"&>
		<p>For a component in an inheritance chain (i.e. via %flags or via autohandlers), the inheriting component. For a subcomponent or method, returns the parent of the owning (file-based) component.   Inheritance is described in <&formatting.myt:link, path="inheritance"&>.</p>
		</&>
		
		<&|formatting.myt:member_doc, name="path"&>
		<p>The URI corresponding to the component.  For this component its "<% self.path %>".  For a subcomponent or method, it is the URI of the owning (file-based) component.</p>
		</&>


		<&|formatting.myt:member_doc, name="request_args"&>
		A list of argument names, corresponding to variable names in the request-scoped <% '<%args scope="request">' %> section, which do have a default value specified.
		</&>

		<&|formatting.myt:member_doc, name="required_args"&>
		A list of argument names, corresponding to variable names in the component-scoped <% '<%args>' %> section, which do not have a default value specified., i.e. they are required component arguments.
		</&>

		<&|formatting.myt:member_doc, name="required_request_args"&>
		A list of argument names, corresponding to variable names in the request-scoped <% '<%args scope="request">' %> section, which do not have a default value specified, i.e. are required request arguments.
		</&>

		<&|formatting.myt:member_doc, name="required_subrequest_args"&>
		A list of argument names, corresponding to variable names in the subrequest-scoped <% '<%args scope="subrequest">' %> section, which do not have a default value specified, i.e. are required subrequest arguments.
		</&>

		<&|formatting.myt:member_doc, name="subrequest_args"&>
		A list of argument names, corresponding to variable names in the subrequest-scoped <% '<%args scope="subrequest">' %> section, which do have a default value specified.
		</&>

	</&>		

	</&>
</&>

