<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="globals", description="Standard Global Variables"&>
	<p>Myghty templates and components always have access to a set of global variables that are initialized on a per-request basis.  The Myghty request object <i>m</i> is always available, as are the component arguments <i>ARGS</i>.  When running with any HTTPHandler-based environment, the HTTP request object <i>r</i> is also available, which in mod_python is the actual mod_python request object, else it is a compatible emulating object.  The Myghty session object, or mod_python's own session object, may be configured to be available as the variable <i>s</i>.  Finally, any set of user-configured global variables can be defined as well; the value of these globals can be specified on a per-interpreter or per-request basis.</p>
	
	<&|doclib.myt:item, name="globalm", description="Your Best Friend: <i>m</i>"&>
	<p><i>m</i> is known as the "request", which represents the runtime context of the template being executed.  Its not the same as the HTTP-specific request object <i>r</i> and is mostly agnostic of HTTP.  <i>m</i> includes methods for handling output and writing content, calling other components, as well as other services that a template will usually need.  The full list of request methods is described in <&formatting.myt:link, path="request"&>.
	</p>

	</&>
	<&|doclib.myt:item, name="globalargs", description="Your Other Best Friend: <i>ARGS</i>"&>
	<p>ARGS represents a dictionary of all arguments sent to the current component.  While a component can specify arguments to be available in the component's namespace via the <% "<%args>" %> tag, the ARGS dictionary contains all arguments supplied to a component regardless of them being named in the <% "<%args>" %> section or not.</p>
	
	<p>In the case of a top-level component called in an HTTP context, ARGS contains the full set of client request parameters.  Each field is one of: a string, a list of strings, or for handling file upload objects, a Field object (from the FieldStorage API) or a list of Field objects.</p>
	
	<p>For components called by other components, ARGS contains all the arguments sent by the calling component. </p>
	
	<p>In all cases, the HTTP request arguments, or whatever arguments were originally sent to the request, are available via the request member <&formatting.myt:link, path="request_members", member="request_args" &>.

	<p>Component arguments are described in <&formatting.myt:link,path="components_args"&>.</p>
	</&>
	<&|doclib.myt:item, name="globalr", description="Your Pal: <i>r</i>"&>
	<p>When running Myghty with any of the HTTPHandlers, i.e. ApacheHandler, CGIHandler, WSGIHandler, or HTTPServerHandler,  variable <i>r</i> is a reference to either the mod python request object or a compatible emulation object.  In the case of ApacheHandler, it is the actual mod_python request.  In other cases, it attempts to provide a reasonably compatible interface, including the member variables headers_in, headers_out, err_headers_out, args, content_type, method, path_info, and filename (more can be added...just ask/submit patches).  The request object is useful applications that need awareness of HTTP-specific concepts, such as headers and cookies, beyond what the more generic <i>m</i> object provides which attempts to be largely agnostic with regards to HTTP.</p>
<p>
Under WSGIHandler, <i>r</i> also contains the member variables <span class="codeline">environ</span> and <span class="codeline">start_response</span>, so that an application may also have direct access to WSGI-specific constructs if needed.
</p>
	</&>
	<&|doclib.myt:item, name="globals", description="Your Fair Weather Friend: <i>s</i>"&>
	<p><i>s</i> references the Myghty session object.  It can also be configured to reference the mod_python session object when running with mod_python 3.1   To use <i>s</i>, you need to turn it on via <& formatting.myt:link, path="session_options", param="use_session" &>.
	</p>
	<p>The Myghty session is still available even if <i>s</i> is not configured. See the section <&formatting.myt:link, path="session"&> for full information on the session object.
	</&>
	<&|doclib.myt:item, name="globalcustom", description="Make your Own Friends"&>
	<p>Myghty supports the addition of any number of global variables that will be compiled into the namespace of all templates.  The value of these variables can be specified on a per-application basis or a per-request basis.  As of version 0.98, both scopes can be used simultaneously.  Per-application globals can be specified via the initial interpreter configurational parameters, or within the httpd.conf file in a mod_python environment.  Per-request globals require that the variables be initialized before the Myghty request begins, which requires programmatic "chaining" to the Interpreter via the methods described in <& formatting.myt:link, path="configuration_programmatic" &>.
	</p>
	
	<p>The two configuration parameters to add global arguments are <&|formatting.myt:codeline&>allow_globals</&>, which specifies a list of global variable names to compile into templates, and <&|formatting.myt:codeline&>global_args</&>, which is a dictionary containing the names of the variables mapped to their desired values.  A basic example of programmatic global variables looks like:
	</p>

	<&|formatting.myt:code, syntaxtype="python" &>
		import myghty.http.WSGIHandler

		def application(environ, start_response):
		
			handler = myghty.http.WSGIHandler.get_handler(
		        allow_globals = ['myglobal'],
				component_root='/path/to/htdocs', 
				data_dir='/path/to/datadirectory'
			)
			
			return handler.handle(
				    environ, 
				    start_response,
				    global_args = {'myglobal' : 'hi'}
            )
	</&>

        <p>Above, all Myghty components will have access to the global variable "myglobal" which has a per-request value of "hi".  Note that the <span class="codeline">allow_globals</span> parameter is only used on the first request, when constructing a new Interpreter object, whereas <span class="codeline">global_args</span> may be specified for each request.</p>

        <p>Another example, using Interpreter:</p>
        <&|formatting.myt:code, syntaxtype="python"&>
        interpreter = interp.Interpreter(
        	allow_globals = ['myglobal'],
        	data_dir = '/path/to/datadir',
        	component_root = '/foo/components',
        )

        interpreter.execute("file.myt", 
        	global_args = {'myglobal':MyGlobalThingy()}
        )
        </&>

        <p>Here is an ApacheHandler example which specifies globals within both scopes:</p>

        <&|formatting.myt:code, syntaxtype="python"&>
        import myghty.http.ApacheHandler as ApacheHandler

        # create per-application global object
        appglobal = 'myappglobal'
        
        def handle(req):
        	# create per-request global object
        	myglob = MyGlobal(req)
        	
            handler = ApacheHandler.get_handler(
        	        req, 
        	        allow_globals = ['appglobal', 'myglobal'],
        	        global_args = {'appglobal' : appglobal}
        	)
        	        
        	return handler.handle(req, global_args = {'myglobal':myglob})
        </&>

        <p>Here is an application-scoped global added in a mod_python environment via the httpd.conf file:</p>
	<&|formatting.myt:code, syntaxtype="conf"&>
		# specify list of global variable names
 		PythonOption MyghtyAllowGlobals ['myglobal']

		# specify the value of the global variable
		PythonOption MyghtyGlobalArgs "{'myglobal':  <% "\\" %>
			__import__('mystuff.util').util.MyGlobalThingy()}"
	</&>

	<&|doclib.myt:item, name="assignment", description="Assignment to Request-Scoped Globals"&>
	<p>When the <span class="codeline">allow_globals</span> configuration parameter specifies global variables to be compiled into all templates, if the variable is not present at request time, it is assigned the value of <span class="codeline">None</span> (as of 0.98a).  This is handy for global variables whos value is not determined until within a request.
	</p>
	
	<p>To assign to a global variable, use <span class="codeline">m.global_args</span>:</p>
        <&|formatting.myt:code&><%text>
	# assume the configuration parameter global_args = ['x','y','z'] is set
	<& hi &>
	% m.global_args['x'] = 'im x!'
	% m.global_args['y'] = 'im y!'
	<& hi &>

	<%def hi>
		x is '<% x %>'
		y is '<% y %>'
		z is '<% z %>'
	</%def>

	</%text></&>
	
	<p>this will produce:
	</p>
	
        <&|formatting.myt:code&>
	x is: ''
	y is: ''
	z is: ''
	x is: 'im x!'
	y is: 'im y!'
	z is: ''
	</&>	
	</&>
	
	</&>	
</&>


