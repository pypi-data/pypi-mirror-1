<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="request", description="The Request"&>

	<p>The Request, available in all Myghty templates as the global variable <i>m</i>, is the central processor of a component and all the calls it makes to other components.  Following are all the useful methods and members of a request. </p>

<p><b>Note:</b> many request methods have been converted to straight data members as of version 0.96, such as get_base_component(), get_request_args(), get_dhandler_arg(), etc.  These methods are still present for existing applications but their use is deprecated.  Their functionality can be located in the Request Members section.</p>


	<&|doclib.myt:item, name="methods", description="Request Methods"&>
	
	<&|formatting.myt:paramtable&>
		<&|formatting.myt:function_doc, name="abort", arglist=['status_code = None']&>
		<p>Halts the currently executing component, and optionally sends the specified HTTP status code.  Any content that is still in the output buffer is discarded.  If the status code is None, the request simply ends with no further output, and the HTTP code 200:OK is returned as a normal request. </p>

	<p>Abort can be used to send any HTTP status code desired to the client.  However, to send a soft redirect via a subrequest, or a hard redirect via the "Location:" header along with 302:Moved, its easier to use m.send_redirect(), described below.  
	</p></&>

		<&|formatting.myt:function_doc, name="apply_escapes", arglist=['text', 'flags'] &>
		programmatically applies escape flags to the given text, the same as they would be used inside of a substitution.  <i>text</i> is a string to be processed, and <i>flags</i> is an array of single-character escape flags.  The two built in flags are "u" for url escaping and "h" for HTML escaping, and user-defined flags are supported as well. See <&formatting.myt:link, path="filtering_escaping", &> for more information on escape flags.</&>


		<&|formatting.myt:function_doc, name="cache", alt="get_cache", arglist=['component=None', 'cache_type=None', 'cache_container_class=None', "**params"]  &>
		<p>Returns the cache for the current component, or if called with an optional component argument, returns the cache for the specified component.  If the cache does not yet exist within the scope of the current request, it will be created using the given list of arguments, else the arguments are disregarded and the previous request-scoped cache interface is returned (note that multiple instances of a cache interface may all reference the same underlying data store, if they are of the same type).  The arguments here override those set in the global configuration for the interpreter, but will usually not override the arguments specified in the %flags section of the component.</p>

<p>The cache type defaults to 'dbm' if a data_dir is in use, else uses 'memory'.  Additional arguments can be added that are specific to MemoryContainer, DBMContainer, or other custom types of containers.  See the section <&formatting.myt:link, path="caching" &>.
		</&>

		<&|formatting.myt:function_doc, name="cache_self", arglist=['component=None', 'key=None', 'retval=None', 'cache_type=None', 'cache_container_class=None', "**params"]  &>
		<p>Caches the current component (or the specified component's) output and return value.  All arguments are optional.  The component argument is a component argument specifying a component other than the currently executing component.  The key argument is the key to store the information under, which defaults to the string "_self".  The key can be modified if you want to cache the comopnent's output based on some kind of conditional information such as component arguments.  The retval argument is a <b>value</b> object which can be used to receive the return value of the component.  The rest of the parameters are the same as those for the cache/get_cache method.</p>
<p>
The function returns True indicating that the retval has been populated and the component's output has been flushed to the output, or False indicating that the value is not yet cached (or needs refreshing) and execution should continue on into the rest of the component.  See <&formatting.myt:link, path="caching" &> for an example.
</p>
		</&>

		<&|formatting.myt:function_doc, name="callers", arglist=["index = None"]  &><p>Returns a single component from the call stack object indicated by the given index, or if None returns the full list of components stored within the current call stack.</p>
		</&>

		<&|formatting.myt:function_doc, name="caller_args", arglist=["index = None"]  &><p>Returns a single dictionary of component arguments from the call stack object indicated by the given index, or if None returns the full list of argument dictionaries sent to each component stored within the current call stack.</p>
		</&>

		<&|formatting.myt:function_doc, name="call_content"  &>
		<p>Similar to the content() method used within a component call with content, except does not push a new buffer onto the buffer stack.  When combined with programmatic pushing and popping buffers onto the request via push_buffer() and pop_buffer(), it can be used for complicated content-grabbing schemes.  For advanced usage.</p>
		</&>
		
		<&|formatting.myt:function_doc, name="call_next", arglist=["**params"]  &>
		Within a chain of inheriting pages, calls the next component in the inheritance chain, i.e. the "wrapped" component.  See <&formatting.myt:link, path="inheritance", &> for more information on the inheritance chain.  Optional **params specify arguments that will override the subclass-component's default argument list on a parameter-by-parameter basis.</&>


		<&|formatting.myt:function_doc, name="call_stack", arglist=["index = None"]  &><p>Provides access to the current call stack.  The call stack is a list of StackFrame objects, which are internal representations of components calling each other.  Each StackFrame object contains the fields "component", "args", "base_component", "content", "is_call_self", and "filter".  The given index refers to what index within the stack to return; if it is <span class="codeline">None</span>, the entire call stack is returned.
		</p>
		</&>
		
		<&|formatting.myt:function_doc, name="comp", arglist=['component', '**params'] &>
		calls a component, subcomponent, or method.   
		See <&formatting.myt:link, path="components_programmatic_comp", &>.
		</&>

		<&|formatting.myt:function_doc, name="component_exists", arglist=['path'] &>
		returns True if the specified file-based component, identified by its URI, can be located.  Performs the full filesystem check even if the requested component is already loaded, therefore repeated calls to this method can get expensive.</&>

		<&|formatting.myt:function_doc, name="content", arglist=[] &>
		returns the content of an embedded component call in the context of a component call with content.  See <&formatting.myt:link, path="components_callwithcontent", &>.
		</&>

		<&|formatting.myt:function_doc, name="create_subrequest", arglist=['component', "resolver_context='subrequest'", '**params'] &>
		Creates a subrequest, which is a child request to this one.  The request can then serve a new component call, which will be serviced within the same output stream as this one.  By default, the subrequest is configured in much the same way as the originating request.  The **params dictionary can be used to override individual configuration parameters; any per-request parameter listed in <&formatting.myt:link, path="parameters", &> is relevant.

		<p>Users will usually prefer to use the methods make_subrequest() or subexec() since they are more compact for typical component-call scenarios.  See <&formatting.myt:link, path="components_programmatic_subrequests", &>.</p>

		<p>Also see <&formatting.myt:link, path="resolver_context"&> for information on the resolver_context parameter.</p>
		</&>


		
		<&|formatting.myt:function_doc, name="decline"&>
		Used by a dhandler to forego processing a directory request, and to bump the interpreter up to the enclosing directory, where it will search again for a dhandler.
		See <&formatting.myt:link, path="specialtempl_dhandler"&>.
		</&>
		

		<&|formatting.myt:function_doc, name="execute"&>
		Executes this request.  Chances are you are already inside the execute call, which can only be called once on any given request object.  However, if you make yourself a subrequest, then you can call execute on that object.  See <&formatting.myt:link, path="components_programmatic_subrequests", &>.
		</&>

		<&|formatting.myt:function_doc, name="execute_component", arglist=["component", "args = {}", "base_component = None", "content = None", "store = None", "is_call_self = False"] &>
		The base component-calling method, at the root of all the other component calling methods (i.e. execute(), comp(), subexec(), etc.).  The richer argument set of this method is useful for calling components with an embedded content call, and also for supplying a custom output buffer to capture the component output directly.  The parameters are:
			<ul>
				<li>component - the string name/URI of the component, or an actual component argument
				<li>args - dictionary of arguments sent to the component.  this is supplied to the component via <i>ARGS</i> as well as via the component-scoped <% "<%args>" %> tag.
				<li>base_component - the base component for the component call.  This is best left as None, where it will be determined dynamically.
				<li>content - reference to a function that will be attached to the <span class="codeline">m.content()</span> method inside the component call.  this is used to programmatically call a "component call with content".  The function takes no arguments and is normally a "closure" within the span of the code calling the enclosing component.
				<li>store - reference to a buffer, such as a file, StringIO, or myghty.buffer object, where the component's output will be sent.
				<li>is_call_self - used internally by the <span class="codeline">m.call_self()</span> method to mark a stack frame as the original "self caller".  Just leave it as False.
			</ul>
		</p>
		<p>Example: component call with content:</p>
		<&|formatting.myt:code&><%text>
			<%def testcall>
				this is testcall.  embedded content:
				[ <% m.content() %> ]
			</%def>
			
			<%python>
				def mycontent():
					m.write("this is the embedded content.")
					
				m.execute_component('testcall', args = {}, content = mycontent)
			</%python>
		</%text></&>
		<p>This will produce:</p>
		<&|formatting.myt:code&><%text>
			this is testcall.  embedded content:
			[ this is the embedded content. ]
		</%text></&>

		</&>

		<&|formatting.myt:function_doc, name="fetch_all" &>
		Returns a list of the full "wrapper chain" of components inheriting each other, beginning with the current inheriting component and going down to the innermost component.  Each element is popped of the request's internal wrapper stack.  See <&formatting.myt:link, path="inheritance"&> for details on component inheritance.
		
		</&>
				
		<&|formatting.myt:function_doc, name="fetch_component", arglist=['path', "resolver_context='component'", 'raise_error=True']&>
		<p>Returns a component object corresponding to the specified component path.  This path may be:</p>

	<ul>
		<li>a URI path relative to one of the application's configured component roots, with an optional clause ":methodname" indicating a method to be called from the resulting file-based component.
		<li>one of the special names SELF, PARENT, REQUEST, with an optional clause ":methodname" indicating a method to be called from the resulting file-based component, or the current subcomponent's owner in the case of a subcomponent that calls SELF.
		<li>the name of a method component stated in the form "METHOD:modulename:classname".
	</ul>

	When the component is located, it will be compiled and/or loaded into the current Python environment if it has not been already.  In this way it is the Myghty equivalent of "import".</p>
<p>If the component cannot be located, it raises a <&|formatting.myt:codeline&>myghty.exceptions.ComponentNotFound</&> error,  unless raise_error is <span class="codeline">False</span>, in which case the method returns <span class="codeline">None</span>.
</p>

	<p>More details on how to identify components can be found in <&formatting.myt:link, path="components"&>.</p>
		<p>Also see <&formatting.myt:link, path="resolver_context"&> for information on the resolver_context parameter.</p>
		</&>

		<&|formatting.myt:function_doc, name="fetch_lead_component", arglist=['path']&>
		<p>Fetches a component similarly to fetch_component(), but also resolves directory requests and requests for nonexistent components to dhandlers.</p>
<p>If the component cannot be located, or a useable dhandler cannot be located because either no dhandler was found or all valid dhandlers have already sent decline() within the span of this request,  a <&|formatting.myt:codeline&>myghty.exceptions.ComponentNotFound</&> error is raised.
</p>
		</&>

		<&|formatting.myt:function_doc, name="fetch_module_component", arglist=['moduleorpath', 'classname', 'raise_error=True']&>
		<p>Fetches a module component.  The value of "moduleorpath" is either a string in the form "modulename:classname", or it is a reference to a Python module containing the desired component.  In the latter case, the argument "classname" must also be sent indicating the name of the desired class to load.
</p>
<p>
Using this method with a string is the same as using the fetch_component() method using the syntax "METHOD:modulename:classname".  
</p>
<p>If the module component cannot be located, a <&|formatting.myt:codeline&>myghty.exceptions.ComponentNotFound</&> error is raised, unless raise_error is <span class="codeline">False</span>, in which case the method returns <span class="codeline">None</span>.

</p>
		</&>
		
		<&|formatting.myt:function_doc, name="fetch_next" &>
		Within a chain of inheriting pages, this method returns the next component in the inheritance chain (also called the "wrapper" chain), popping it off the stack.  The component can then be executed via the <&|formatting.myt:codeline&>m.comp()</&> or similar method.  See the section <&formatting.myt:link, path="inheritance", &>.
		</&>
		

		<&|formatting.myt:function_doc, name="get_session", arglist=['**params']&><p>Creates or returns the current Myghty session object (or optionally the mod_python Session object).  If the session has not been created, the given **params are used to override defaults and interpreter-wide configuration settings during initialization.</p>
	<p>Details on the Session are described in <&formatting.myt:link,path="session"&>.
	</p>
		</&>

		
		<&|formatting.myt:function_doc, name="has_content"&>
		Inside of a subcomponent or method call, returns whether or not the component was a component call with content.  See the section <&formatting.myt:link, path="components_callwithcontent", &>.
		</&>

		<&|formatting.myt:function_doc, name="has_current_component"&>
		Returns True if this request has a currently executing component.  This becomes true once a request's execute() method has been called.
		</&>
		
		<&|formatting.myt:function_doc, name="instance"&>
		This static method returns the request corresponding to the current process and thread.   You can access the current request in a globally scoped block via this method.  See <&formatting.myt:link, path="scopedpython_global"&>.
		
		<&|formatting.myt:code&><%text>
		<%python scope="global">
			req = request.instance()
		</%python>
		</%text></&>
		
		
		</&>
		<&|formatting.myt:function_doc, name="is_subrequest"&>
		Returns True if the currently executing request is a subrequest.  See the section <&formatting.myt:link, path="components_programmatic_subrequests", &>.
		</&>

		<&|formatting.myt:function_doc, name="log", arglist=['message'] &>
		Logs a message.  The actual method of logging is specific to the underlying request implementation; for standalone and CGI it is the standard error stream, for mod_python it is a [notice] in the Apache error log.
		</&>
		
		<&|formatting.myt:function_doc, name="make_subrequest", arglist=['component', '**params'] &>
		Creates a new subrequest with the given component object or string path <i>component</i> and the request arguments <i>**params</i>.  The returned request object can then be executed via the execute() method.   See <&formatting.myt:link, path="components_programmatic_subrequests", &>.
		</&>
		
		<&|formatting.myt:function_doc, name="scomp", arglist=['component', '**params']&>
		Executes a component and returns its content as a string.  See <&formatting.myt:link, path="components_programmatic_scomp", &>.
		
		</&>
		
		<&|formatting.myt:function_doc, name="send_redirect", arglist=['path', 'hard=True']&>
		Sends a hard or soft redirect to the specified path.  A hard redirect is when the http server returns the "Location:" header and instructs the browser to go to a new URL via the 302 - MOVED_TEMPORARILY return code.  A soft redirect means the new page will be executed within the same execution context as the current component.  In both cases, the current component is aborted, and any buffered output is cleared.  For this reason, if auto_flush is enabled (which it is not by default), you would want to call this method, particular the soft redirect, only before any content has been output, most ideally in an %init section.  If auto_flush is disabled, you can call either version of this method anywhere in a component and it will work fine.
		</&>

		<&|formatting.myt:function_doc, name="set_output_encoding", arglist=['encoding', 'errors="strict"']&>
		<p>Change the output_encoding, and, optionally, the encoding error handling strategy.</p>
		<p>Generally, you will not want to change the output encdoing after you have written any output (as then your output will be in two different encodings --- probably not what you wanted unless, for example, you are generating Mime multipart output.)</p>
		<p>See the section on <&formatting.myt:link, path="unicode"&> for further details.</p>
		</&>
		
		<&|formatting.myt:function_doc, name='subexec', arglist=['component', '**params']&>
		All-in-one version of <&|formatting.myt:codeline&>make_subrequest</&> and 
		<&|formatting.myt:codeline&>m.execute()</&>.  See <&formatting.myt:link, path="components_programmatic_subrequests", &>.
		
		</&>
		
		
		<&|formatting.myt:function_doc, name='write', args=['text'], alt='out'&>
		Writes text to the current output buffer.  If auto_flush is enabled, will flush the text to the final output stream as well.
		</&>
	</&>
	
	</&>
	
	<&|doclib.myt:item,name="members", description="Request Members" &>

	<&|formatting.myt:paramtable&>


		<&|formatting.myt:member_doc, name="attributes", &>
		<p>A dictionary where request-local information can be stored.  Also can be referenced by the member <&formatting.myt:link, member="notes"&>.  If the request is a subrequest, this dictionary inherits information from its parent request.</p>
		</&>

		<&|formatting.myt:member_doc, name="base_component" &>
Represents the "effective" file-based component being serviced, from which methods and attributes may be accessed.  When autohandlers or other inherited components are executing, this member always points to the file-based component at the bottom of the inheritance chain.  This allows an inherited component to access methods or attributes that may be "dynamically overridden" further down the inheritance chain.  It is equivalent to the special path <span class="codeline">SELF</span>.  When a method or def component is called via the path of another file-based component, base_component will change to reflect that file-based component for the life of the subcomponent call.</&>

		<&|formatting.myt:member_doc, name="current_component" &>
		The component currently being executed.  Within the body of a component, this is equivalent to <span class="codeline">self</span>.
		</&>
		
		<&|formatting.myt:member_doc, name="dhandler_path", &>
		In the case of a dhandler call, the request path adjusted to the current dhandler. 
		<p>For information on dhandlers see <&formatting.myt:link, path="specialtempl_dhandler"&>.</p>
		</&>

		<&|formatting.myt:member_doc, name="encoding_errors", &>
		<p>The current output encoding error handling strategy.  This is a read-only attribute, though you may change it using the <&formatting.myt:link, path="request_methods", method="set_output_encoding" &> method.</p>
		<p>See the section on <&formatting.myt:link, path="unicode"&> for further details.</p>
		</&>

		<&|formatting.myt:member_doc, name="global_args", &>
		<p>A dictionary of custom-configured global variables to be used throughout the request.  Global variables can be initialized or re-assigned here, and the new value will become available to all further component calls.  Each key in this dictionary must already correspond to a value in the <span class="codeline">allow_globals</span> configuration parameter.  See <&formatting.myt:link, path="globals_globalcustom" &> for full examples.</p>
		</&>

		<&|formatting.myt:member_doc, name="interpreter", &>
		<p>The Interpreter object that created this Request object.</p>
		</&>

		<&|formatting.myt:member_doc, name="notes", &>
		A synonym for <& formatting.myt:link, member="attributes"&>.
		</&>

		<&|formatting.myt:member_doc, name="output_encoding", &>
		<p>The current output encoding.  This is a read-only attribute, though you may change it using the <&formatting.myt:link, path="request_methods", method="set_output_encoding" &> method.</p>
		<p>See the section on <&formatting.myt:link, path="unicode"&> for further details.</p>
		</&>

		<&|formatting.myt:member_doc, name="parent_request", &>
		In a subrequest call, refers to the immediate parent request of this request, else defaults to None.
		</&>

		<&|formatting.myt:member_doc, name="request_args" &>
		<p>A dictionary containing the initial request arguments sent when this request was created.  In an HTTP context, this usually refers to the request arguments sent by the client browser.  </p>
		
		<p>In the case of a subrequest (described in <&formatting.myt:link, path="components_programmatic_subrequests" &>), this member refers to the request arguments sent to the local subrequest.  To get the original request arguments, use the root_request_args parameter.</p>
		
		<p>For detailed description of component and request arguments, see <&formatting.myt:link, path="components_args"&>.</p>
		</&>

		<&|formatting.myt:member_doc, name="request_component" &>
		Returns the top-level component corresponding to the current request.
		</&>

		<&|formatting.myt:member_doc, name="request_path", &>
		<p>The original path sent to this request for resolution.  In the case of a subrequest, the path sent to the subrequest. </p>
  
		<p>In the case of a new request that is called with a pre-existing component object, such as in a custom application interfacing to the Myghty interpreter, the request_path defaults to None, but can also be set programmatically via the <&formatting.myt:link, path="parameters", param="request_path"&> configuration argument.</p>
				
		</&>

		<&|formatting.myt:member_doc, name="root_request" &>
		Refers to the ultimate originating request in a string of subrequests.
		If this request is not a subrequest, this member references the current request.
		</&>

		<&|formatting.myt:member_doc, name="root_request_args" &>
		<p>Used in subrequests, returns the request arguments sent to the ultimate root request in a chain of subrequests.  For a regular request with no parent, this dictionary is synonymous with request_args.  
	 </p>
		
		<p>For detailed description of component and request arguments, see <&formatting.myt:link, path="components_args"&>.</p>
		</&>


		<&|formatting.myt:member_doc, name="root_request_path", &>
		<p>The request path for the original root request, in a chain
		of subrequests.</p>				
		</&>

	</&>
	</&>
</&>
