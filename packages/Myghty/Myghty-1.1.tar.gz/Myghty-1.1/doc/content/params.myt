<%flags>inherit='document_base.myt'</%flags>
	<&|doclib.myt:item, name="parameters", description="Index of Configuration Parameters", header="Appendix" &>
	
	<p>Configuration parameters in Myghty are basically a big dictionary of data that is initially passed to the constructor for <span class="codeline">myghty.interp.Interpreter</span>, which represents the entry point for running a Myghty template.  Upon construction, the Interpreter instantiates all the other objects
	it needs, such as the Compiler, the Resolver, and a prototype Request object (a prototype is an object that is used as a template to make copies of itself), passing in the same hash of configuration parameters.  Each object takes what it needs out of the dictionary.</p>
	
	<p>If you are writing your own interface to <span class="codeline">Interpreter</span>, such as a standalone or simple CGI client, you can pass one or more of these values programmatically to the constructor of the Interpreter.  If running from mod python, values can be specified in the http.conf file using the format <span class="codeline">Myghty&lt;<i>Name</i>&gt;</span>, where <i>Name</I> is the parameter name in InitialCaps format (i.e., data_dir becomes DataDir).
	</p>
	
	<p>Note also that there are configuration parameters specific to the caching mechanism, listed in <&formatting.myt:link, path="caching_options"&>, as well as session specific parameters listed in <&formatting.myt:link, path="session_options"&>.</p>
	
	<&|formatting.myt:paramtable&>
	<&|formatting.myt:param, name="allow_globals", classname="Compiler", type="list of strings", users="developers" &>
	A list of global variable names that will be compiled into Myghty templates, and will be expected to be provided upon template execution.  The variable "r", representing the Apache Request, is delivered to templates via this parameter.  To add your own variables, specify their names in this list, and also specify it as a key in the RequestImpl argument global_args to provide the values.
	See the section <&formatting.myt:link, path="globals_globalcustom", text="Make your Own Friends"&> for details.
	</&>

	<&|formatting.myt:param, name="attributes", classname="Interpreter", type="dictionary", users="all" &>
	A dictionary of data that will be stored by the Interpreter used throughout a particular Myghty application.  This is a way
	to set per-application global variables.  The values are accessible via the <span class="codeline">interpreter.attributes</span> 
	dictionary.  </p>
	<&|formatting.myt:code, syntaxtype="python"&><%text>
		i = interp.Interpreter(attributes = {'param': 'value'})
	</%text></&>
	Accessing attributes:	
	<&|formatting.myt:code, syntaxtype="python"&><%text>
		# call interpreter off request,
		# and get an attribute
		p = m.interpreter.attributes['param']
		
		# call interpreter off component,
		# and set an attribute
		self.interpreter.attributes['param'] = 'value'
	</%text></&>
	
	<p>Interpreter attributes can be compared to component <&formatting.myt:link, path="components_members", member="attributes"&>, as well
	as request <&formatting.myt:link, path="request_members", member="attributes"&>.
	</p>
	</&>

	<&|formatting.myt:param, name="auto_flush", classname="Request", type="boolean", default="False", users="developers" &>
	<p>Whether or not <&|formatting.myt:codeline&>m.write</&> calls will be automatically flushed to the final output stream as they are called, or will be buffered until the end of the request.  Autoflush being on makes things a little more tricky, as you can't do any kind of page redirects (neither external nor internal) once the content starts coming out.  Error messages become messy as well since they are similar to an internal redirect.</p>
	<p>Autoflush can be set in a variety of ways and is described fully in the section <&formatting.myt:link,path="filtering_autoflush"&>.
	</p>
	</&>


	<&|formatting.myt:param, name="auto_handler_name", classname="Interpreter", type="string", default="autohandler", users="administrators" &>
	The name of the file used as a global page wrapper, defaults to 'autohandler'.  See the section <&formatting.myt:link, path="specialtempl_autohandler", text="autohandlers" &> for information on autohandlers.
	</&>


	<&|formatting.myt:param, name="cache_debug_file", classname="Cache", type="file object", version="0.94", default="None", users="optimizers" &>
	If pointing to a Python file object, container operations performed by the caching system will be logged, allowing the viewing of how often data is being refreshed as well as how many concurrent threads and processes are hitting various containers.
	When running with ApacheHandler or CGIHandler, this parameter can be set to the standard Apache log via the 
	parameter <&|formatting.myt:codeline&>log_cache_operations</&>.
	</&>


	<&|formatting.myt:param, name="code_cache_size", classname="Interpreter", type="integer", default="16777216", users="optimizers" &>
	Size of the cache used by Interpreter to cache loaded component objects, measured in bytes.  The cache works on a "least recently used" scheme.  This value has a great impact on performance, as too large a value can use up lots of memory for a very large site, and too small results in excessive "swapping" of components in and out of memory.  Cache operations can be logged via <&formatting.myt:link, param="debug_file" &>.  
	</&>

	<&|formatting.myt:param, name="compiler", classname="Interpreter", type="object", default="myghty.compiler.Compiler", users="hackers" &>
	An instance of <&|formatting.myt:codeline&>myghty.compiler.Compiler</&> used to generate object files.  Not much reason to play with this unless you are seriously hacking your own engine.  The default Compiler object will receive its optional parameters from the argument list sent to the constructor for <&|formatting.myt:codeline&>Interpreter</&>.
	</&>


	<&|formatting.myt:param, name="component_root", classname="Resolver", type="string or list", default="None", users="all" &>
	<p>This parameter is almost always required; it is the filesystem location, or list of locations, with which to locate Myghty component files.  </p>
	<p>The two formats of component_root are as follows:</p>
	<p>Single string</p>
	<&|formatting.myt:code, syntaxtype="python"&>component_root = "/web/sites/mysite/htdocs"</&>
	<p>List of hashes</p>
	<&|formatting.myt:code, syntaxtype="python"&>component_root = [
		{'main':"/web/sites/mysite/htdocs"},
		{'components':"/web/sites/mysite/components"},
		{'alt':"/usr/local/lib/special-comp"}
	]
	</&>

	<p>The single string specifies one root for all component calls, which will be assigned the identifying key "main".  The list of hashes specifies the keys and paths for a collection of locations which will be searched in order for a component.  This allows you to have one file tree that is web-server accessible files, and another file tree that contains files which can only be used as embedded components, and can't be accessed by themselves.  The key names are used to uniquely identify a component by both its location and its name, such as "main:/docs/index.myt".</p>
	
	<p>For examples of component_root configuration, see the section <& formatting.myt:link, path="configuration" &>.  For advanced options on file-based resolution, see <& formatting.myt:link, path="resolver" &>.
	</p>
	</&>


	<&|formatting.myt:param, name="data_dir", classname="Interpreter", type="string", default="None", users="all" &>
	Directory to be used to store compiled object files (.py files and .pyc files), lock files used for synchronization, as well as container files which store data for the component caching system and the session object.  A non-None value implies True for the "use_object_files" setting.  Compiled object files are stored in the <span class="codeline">obj</span> directory, and cache/session files are stored underneath <span class="codeline">container_XXX</span> directories.
	</&>

	<&|formatting.myt:param, name="debug_elements", classname="Interpreter", type="list", version="0.97alpha3", default="[]", users="optimizers" &>
	<p>A list of string names that refer to various elements that can send debug information to the Interpreter's debug output.  An example with all allowed names:</p>
	<&|formatting.myt:code, syntaxtype="python"&>
		debug_elements = [
			# all resolution of components
			'resolution', 

			# inspection of component objects and modules loaded into memory and later garbage-collected
			'codecache', 
			
			# inspection of the generation and compilation of components
			'classloading',
			
			# cache operations, reloading of cached data
			'cache', 
		]
	</&>
	
	</&>
	
	<&|formatting.myt:param, name="debug_file", classname="Interpreter", type="file object", version="0.93b", default="stderr", users="optimizers" &>
	<p>References a Python file object; if non-None, the Interpreter will send debugging information to this file.  Note that line breaks are not sent by default; use code such as <span class="codeline">myghty.buffer.LinePrinter(sys.stderr)</span> to wrap the file in a line-based formatter.
	</p>
	<p>When running the Interpreter in an HTTP context, various implementations of HTTPHandler supply their own stream for debugging information, such as the ApacheHandler which supplies the Apache error log as a filehandle.</p>
	<p>As of version 0.97alpha3, to actually enable debug logging requires the <&formatting.myt:link, param="debug_elements"&> parameter to be set up.
	</p>
	</&>


	<&|formatting.myt:param, name="default_escape_flags", classname="Compiler", type="list", default="None", users="developers" &>
	This is a list of escape flags that will be automatically applied to all substitution calls, i.e. <%text>&lt;% <i>string</i> %&gt;</%text>.  See <&formatting.myt:link, path="filtering_escaping"&> for more information on content escaping.
	</&>


	<&|formatting.myt:param, name="dhandler_name", classname="Request", type="string", default="dhandler", users="administrators" &>
	The name of the file used as a directory handler, defaults to 'dhandler'.  See the section <&formatting.myt:link, path="specialtempl_dhandler", text="dhandlers" &> for information on directory handlers.
	</&>

	<&|formatting.myt:param, name="disable_unicode", classname="Request, Compiler", type="boolean", default="False", users="developers", version="1.1" &>
	Disable the new unicode support features.   If set, all strings are assumed to be <span class="codeline">str</span>s in the system default encoding (usually ASCII).
See the section on <&formatting.myt:link, path="unicode"&> for further details.
	</&>

	<&|formatting.myt:param, name="dont_auto_flush_filters", classname="Request", type="boolean", default="False", users="developers" &>
	If auto_flush is turned on, this option will keep auto_flush turned off for components that use <% "<%filter>" | h %> sections.  This is useful if you have filters that rely upon receiving the entire block of text at once.  See the section <&formatting.myt:link, path="filtering_filtering", text=m.apply_escapes("<%filter>", ['h'])&> for more information on filters.
	</&>

	<&|formatting.myt:param, name="encoding_errors", classname="Request", type="string", default="strict", users="developers", version="1.1" &>
<p>Sets the initial value for the <span class="codeline">encoding_errors</span> of requests, which, in turn, determines how character set encoding errors are handled.</p>
<p>Some choices are:</p>
<dl>
    <dt><span class="codeline">strict</span></dt>
    <dd>Raise an exception in case of an encoding error.</dd>
    <dt><span class="codeline">replace</span></dt>
    <dd>Replace malformed data with a suitable replacement marker,
        such as <span class="codeline">"?"</span>.</dd>
    <dt><span class="codeline">xmlcharrefreplace</span></dt>
    <dd>Replace with the appropriate XML character reference.</dd>
    <dt><span class="codeline">htmlentityreplace</span></dt>
    <dd>Replace with the appropriate HTML character entity reference,
      if there is one; otherwise replace with a numeric character reference.
      (This is not a standard python encoding error handler.  It is
      provided by the <span class="codeline">mighty.escapes</span> module.)
    </dd>
    <dt><span class="codeline">backslashreplace</span></dt>
    <dd>Replace with backslashed escape sequence.</dd>
    <dt><span class="codeline">ignore</span></dt>
    <dd>Ignore malformed data and continue without further notice.</dd>
</dl>
<p>See also the section on <&formatting.myt:link, path="unicode"&>,
and the Python <a href="http://docs.python.org/lib/module-codecs.html">codecs</a> documentation.
</p>
	</&>

	<&|formatting.myt:param, name="error_handler", classname="RequestImpl", type="function", default="None", users="developers" &>
	<p>A function object that will be passed all exceptions and given the chance to handle them before regular processing occurs.  The format of the function is:</p>
	<&|formatting.myt:code, syntaxtype="python"&>
	def handle_error(e, m, **params):
		# custom error handling goes here
		# ...

		# return False to continue handling error, True to disregard
		return False
	</&>
	<p>Where 'e' is a <span class="codeline">myghty.exception.Error</span> object and m is the request object.  The global variable 'r' will also be passed if running in an HTTP context.  The function should return True to stop all further error handling, or False to continue error handling as normal.</p>

	<p>
	The request object, while it is the same instance used to handle the request initially, no longer will have any buffered content and will also not have a current component instance.  It is safe to call subrequests from it, allowing the construction of custom error pages.
	</p>

	<p>See also <&formatting.myt:link, param="raise_error"&> to simply raise an error outside the Request and bypass all internal and custom error handling.</p>
	
	</&>
	
	<&|formatting.myt:param, name="escapes", classname="Interpreter", type="dict", default="{'h':html_escape, 'u':url_escape}", users="developers" &>
	<p>Use this parameter to define your own custom escaping functions that are available within substitutions, as well as <&|formatting.myt:codeline&>m.apply_escapes()</&>.  Within a dictionary key/value pair, the key is the identifying character, and the value is a reference to a single-argument function that will be called with the string with which to apply the text escape.  The function should return the filtered text.
	</p>
	
	<p>Escaping is described fully at <& formatting.myt:link, path="filtering_escaping" &>.
	</p>
	</&>


	<&|formatting.myt:param, name="generator", classname="Compiler", type="object", default="myghty.objgen.PythonGenerator", users="hackers" &>
	An instance of <&|formatting.myt:codeline&>myghty.objgen.ObjectGenerator</&> that is used to generate object files.  Again, for the brave hacker, you can write your own generator and output object files in whatever language you like.  
	</&>

	<&|formatting.myt:param, name="global_args", classname="RequestImpl", type="dictionary", users="developers" &>
	A list of global argument names and values that will be available in all template calls.  See the section <&formatting.myt:link, path="globals_globalcustom", text="Make your Own Friends"&> for details.
	</&>

	<&|formatting.myt:param, name="interpreter_name", classname="HTTPHandler", type="string", users="administrators" &>
	<p>Specifies the name of the Myghty interpreter that should be used.  All HTTP handlers modules maintain a dictionary of HTTPHandler instances, each of which references a Myghty interpreter, keyed off of a name.  
	When this name is explicitly specified, that particular handler will be created if it doesnt exist and then used.</p>
	<p>This option is currently most useful for use within multiple Apache directives, so that different sets of configuration parameters can be used for different directives, without requiring the use mod_python's multiple Python interpreters feature.  See the example in <&formatting.myt:link, path="configuration_mod_python_multiple" &>.
	</p>
	</&>

	<&|formatting.myt:param, name="lexer", classname="Compiler", type="object", default="myghty.lexer.Lexer", users="hackers" &>
	An instance of <&|formatting.myt:codeline&>myghty.request.Lexer</&>, used to parse the text of template files.
	</&>

	<&|formatting.myt:param, name="log_cache_operations", classname="ApacheHandler or CGIHandler", version="0.93b", type="boolean", default="False", users="optimizers" &>
	Deprecated; use <&formatting.myt:link, param="debug_elements" &> instead.
	</&>

	<&|formatting.myt:param, name="log_component_loading", classname="ApacheHandler or CGIHandler", version="0.93b", type="boolean", default="False", users="optimizers" &>
	Deprecated; use <&formatting.myt:link, param="debug_elements" &> instead.
	</&>

	<&|formatting.myt:param, name="log_errors", classname="HTTPHandler", type="boolean", default="False", users="administrators" &>
	Specifies whether or not component errors should receive a full stack trace in the Apache error log,  standard error output of CGIHandler, or other HTTP-specific logging system.
	If false, component errors still produce a single-line description of the error in the log.  See also <&formatting.myt:link, param="output_errors"&>.  If <&formatting.myt:link, param="raise_error"&> is set to true, no logging of errors occurs.
	</&>


	<&|formatting.myt:param, name="max_recursion", classname="Request", type="integer", users="optimizers", default="32" &>
	The highest level of component recursion that can occur, i.e. as in recursive calls to a subcomponent.
	</&>


	<&|formatting.myt:param, name="module_components", classname="ResolveModule", type="array of hashes", users="all" &>
	This parameter is used for resolving <& formatting.myt:link, path="modulecomponents" &> using regular expressions which are mapped to function, class or class instance objects.  See <&formatting.myt:link, path="modulecomponents_resolution_module_components"&> for examples.</p>
	</&>


	<&|formatting.myt:param, name="module_root", classname="ResolvePathModule", type="array of hashes", users="all" &>
	This parameter is used for resolving <& formatting.myt:link, path="modulecomponents" &> using file paths which map to the locations of python files and the attributes within. See <&formatting.myt:link, path="modulecomponents_resolution_module_root"&> for examples.</p>
	</&>

	<&|formatting.myt:param, name="module_root_adjust", classname="ResolvePathModule", type="callable", users="all", version="0.99b" &>
	This parameter is used in combination with <& formatting.myt:link, param="module_root" &> to specify a callable that will translate an incoming URI before being resolved to a path-based module.  See <&formatting.myt:link, path="modulecomponents_resolution_module_root"&> for more detail.</p>
	</&>


	<&|formatting.myt:param, name="out_buffer", classname="DefaultRequestImpl", type="object", users="developers" &>
	A Python file object, or similar, with which to send component output.  See the <&formatting.myt:link, path="configuration", text="Configuration"&> section for examples.
	</&>

	<&|formatting.myt:param, name="output_encoding", classname="Request", type="string", default="sys.getdefaultencoding()", users="developers", version="1.1" &>
	Sets the initial value for the <span class="codeline">output_encoding</span> of requests.  The default value is python's system default encoding (usually ASCII.)
See the section on <&formatting.myt:link, path="unicode"&> for further details.
	</&>

	<&|formatting.myt:param, name="output_errors", classname="ApacheHandler or CGIHandler", version="0.93b", type="boolean", default="True", users="administrators" &>
	Specifies whether or not component errors with full stack trace should be reported to the client application.
	If false, component errors will produce a 500 Server Error.  See also <&formatting.myt:link, param="log_errors"&>.  If <&formatting.myt:link, param="raise_error"&> is set to True, this parameter is overridden and client will receive a 500 server error (unless the error is caught by an external handler).
	</&>


	<&|formatting.myt:param, name="parent_request", classname="Request", type="object", users="hackers" &>
	This parameter specifies the parent request when making subrequests, and is automatically provided.  For more information see <&formatting.myt:link, path="components_programmatic", text="Programmatic Interface"&>. 
	</&>

	<&|formatting.myt:param, name="path_moduletokens", classname="ResolvePathModule", type="list of strings", default="['index']", users="all", version="0.99b" &>
	<p>Used by <&formatting.myt:link, param="module_root"&> to specify default path tokens that should be searched in module attribute paths.  See <&formatting.myt:link, path="modulecomponents_resolution_module_root_options"&> for details.
    </&>

	<&|formatting.myt:param, name="path_stringtokens", classname="ResolvePathModule", type="list of strings", default="[]", users="all" , version="0.99b" &>
	<p>Used by <&formatting.myt:link, param="module_root"&> to specify default path tokens that should be searched in file paths.  See <&formatting.myt:link, path="modulecomponents_resolution_module_root_options"&> for details.
    </&>


	<&|formatting.myt:param, name="path_translate", classname="Resolver", type="list of tuples, or a callable", users="administrators" &>
	A list of regular-expression translations that will be performed on paths before they are used to locate a component and/or module component.  This can be useful for complicated web server configurations where aliases point to component roots, or specifying a default document for path requests.  It looks as follows:

	<&|formatting.myt:code, syntaxtype="python"&><%text>
		path_translate = [
				# convert /store/* to /shop/*
				(r'^/store/(.*)', r'/shop/\1'),
				
				# convert /documents/* to /docs/*
				(r'^/documents/', '/docs/'),
				
				# convert /foo/bar/ to /foo/bar/index.myt
				(r'/$', '/index.myt'),
			]
	</%text></&>
	<p>As of revision 0.99b, the argument to path_translate can alternatively be specified as a callable, which converts its given URI to the translated value:</p>
	<&|formatting.myt:code, syntaxtype="python"&><%text>
        def my_translate(uri):
            return "/doc/" + uri
		path_translate = my_translate
	</%text></&>
	
	<p>Note that the <&formatting.myt:link, path="request_members", member="request_path"&> member of the request object will reference the original path before translation, whereas the <&formatting.myt:link, path="components_members", member="path" &> of the component served will contain the translated path (for file-based components).</p>

	<p>More detail about path translation can be found in <&formatting.myt:link, path="resolver" &>.</p>
	</&>

	<&|formatting.myt:param, name="python_post_processor", classname="Compiler", type="function", users="hackers" &>
	References a function that will be invoked with the full text of each individual unit of Python code created during component generation (i.e., creation of .py files).  The returned string will be used as the Python code that is actually placed within the generated .py file.  Also see <&formatting.myt:link, param="text_post_processor" &>.
	</&>


	<&|formatting.myt:param, name="python_pre_processor", classname="Compiler", type="function", users="hackers" &>
	References a function that will be invoked with the full text of a template's source file before it is parsed.  The returned string will then be used as the source to be parsed.  
	</&>

	<&|formatting.myt:param, name="raise_error", classname="Request", version="0.97a", type="boolean", default="False", users="developers" &>
	<p>Indicates if errors should be raised when they occur, or be handled by error handling functionality.  If set to True, no error logging, friendly client response, or custom internal error handler function will happen.  Instead, an external error handler can be used.

This parameter overrides invalidates the functionality of <&formatting.myt:link, param="log_errors"&>, <&formatting.myt:link, param="output_errors"&> and <&formatting.myt:link, param="error_handler"&>.
	</p>
	<p>
	This parameter allows the entire <span class="codeline">interpreter.execute()</span> or <span class="codeline">handler.handle()</span> call to be wrapped in a <span class="codeline">try: / except:</span> block, where the error can be handled externally to all Myghty functionality.
	</p>
	</&>


	<&|formatting.myt:param, name="request", classname="Interpreter", type="object", default="myghty.request.Request", users="hackers" &>
	An instance of <&|formatting.myt:codeline&>myghty.request.Request</&> used as a prototype to generate new requests.  Its context-specific behavior is supplied by a separate instance of <&|formatting.myt:codeline&>myghty.request.RequestImpl</&>, so there is not much reason to change this either.
	</&>



	<&|formatting.myt:param, name="request_impl", classname="Request", type="object", default="myghty.request.DefaultRequestImpl", users="hackers" &>
	An instance of <&|formatting.myt:codeline&>myghty.request.RequestImpl</&> that will be used either as a prototype to create new RequestImpls per request, or can be passed per individual interpreter execution.  RequestImpl tells <&|formatting.myt:codeline&>Request</&> how it should interact with its environment.  Take a look at <&|formatting.myt:codeline&>ApacheHandler.ApacheRequestImpl</&>, <&|formatting.myt:codeline&>CGIHandler.CGIRequestImpl</&>, and <&|formatting.myt:codeline&>myghty.request.DefaultRequestImpl</&> for examples.
	</&>

	<&|formatting.myt:param, name="request_path", classname="Request", type="string", default="myghty.request.Request", users="developers" &>
	Sets the initial request path for this request.  In most cases, this is set automatically by simply calling a request with a string-based component name, or with a file-based component which can return its originating path.  However, in the case of a request being called with a memory or module-based component, the path defaults to None and must be set by the calling function if it is to be referenced by components.
	</&>

	<&|formatting.myt:param, name="require_publish", classname="ResolvePathModule", type="boolean", default="False", users="all", version="0.99b" &>
	<p>Indicates that callables located via <&formatting.myt:link, param="module_root"&> resolution require an attribute named 'public' set to True attached to them, in order to allow access.  See <&formatting.myt:link, path="modulecomponents_resolution_module_root_options"&> for details.
    </&>
    
	<&|formatting.myt:param, name="resolver", classname="Interpreter", type="object", default="myghty.resolver.FileResolver", users="hackers" &>
	An instance of <&|formatting.myt:codeline&>myghty.resolver.Resolver</&> that is used to locate component files.  Both ApacheHandler and CGIHandler have their own instances of <&|formatting.myt:codeline&>Resolver</&> but don't yet do anything special.  If you wanted some kind of special file resolution behavior, you can swap in your own subclass of <&|formatting.myt:codeline&>Resolver</&>.
	</&>


	<&|formatting.myt:param, name="resolver_strategy", classname="Resolver", type="list", users="developers"&>
	Allows configuration of the rules used in component resolution.  See the section <&formatting.myt:link, path="resolver" &> for details.
	</&>


	<&|formatting.myt:param, name="source_cache_size", classname="Interpreter", type="integer", default="1000", users="optimizers" &>
	Size of the cache used by Interpreter to cache the source of components.  See <&formatting.myt:link, param="use_static_source"&> for
	a description of source caching, and see code_cache_size for a description of the LRU caching scheme.
	</&>


	<&|formatting.myt:param, name="text_post_processor", classname="Compiler", type="function", users="hackers" &>
	References a function that will be invoked with the full text of each individual unit of output text created during component generation (i.e., creation of .py files).  The returned string will be used as the output text that is actually placed within the generated .py file.  Also see <& formatting.myt:link, param="python_post_processor"&>.
	</&>


	<&|formatting.myt:param, name="use_auto_handlers", classname="Interpreter", type="boolean", default="True", users="developers" &>
	Whether or not to use autohandlers.  See the section <&formatting.myt:link, path="specialtempl_autohandler", text="autohandlers" &> for more information.
	</&>


	<&|formatting.myt:param, name="use_dhandlers", classname="Request", type="boolean", default="True", users="developers" &>
	Whether or not to use directory handlers.  See the section <&formatting.myt:link, path="specialtempl_dhandler", text="dhandlers" &> for more information.
	</&>


	<&|formatting.myt:param, name="use_object_files", classname="Interpreter", type="boolean", default="True if data_dir is not null", users="optimizers" &>
	Indicates whether or not components should be compiled into module files on the filesystem, or into strings held in memory.  A value of None for the <&formatting.myt:link, param="data_dir"&> parameter will have the same effect.  There is no advantage whatsoever to having components compiled in memory, and startup performance will be degraded for repeated calls to the same component.  It might be useful if you are running the interpreter in a "one shot" fashion where there is no need to have compiled object files lying around.  
	</&>


	<&|formatting.myt:param, name="use_session", classname="ApacheHandler", type="boolean", users="developers" &>
		The additional global variable <i>s</i> to reference the Myghty session, or alternatively 
		the mod_python 3.1 session,
		is turned on when this option is set to True.  See the section <&formatting.myt:link, path="session" &> for details.
	</&>

	<&|formatting.myt:param, name="use_source_line_numbers", classname="Compiler", type="boolean", users="hackers" &>
	Whether or not to put source line numbers in compiled object files.  This is used to generate friendly stack traces upon errors (when that feature is complete).
	</&>


	<&|formatting.myt:param, name="use_static_source", classname="Interpreter, Resolver", type="boolean", default="False", users="optimizers" &>
	This parameter, when set to <span class="codeline">True</span>:  
	<ul>
		<li>Enables URI caching within the resolver, and/or turns on all configured URICache() resolution rules, so that visiting a URI a second time does not produce any filesystem checks, within the currently cached set of URIs.  </li>
		<li>Disables repeated last-modification time checks on all template files and module-component files</li>
		<li>Disables last-modification time checks on compiled template object files against the template they were generated from, which in effect disables re-compilation of templates even across server restarts, unless the object file is removed from the <span class="codeline">obj</span> directory underneath the configured <& formatting.myt:link, param="data_dir"&> directory</li>
	</ul>
	Use use_static_source on production servers where the site's structure is not being changed, to prevent auto-recompilation of modified templates, and to prevent reloads of modified module component modules.  There is both a performance increase due to fewer filesystem checks, and also a stability increase, as no Python modules are dynamically reloaded within a running server.   Dynamic reloads in Python are somewhat error-prone, particularly if a module with a base class changes, and a corresponding subclass in a different, non-reloaded module attempts to instantiate itself.  
	</&>
	</&>




	</&>


