<%flags>inherit='document_base.myt'</%flags>

<&|doclib.myt:item, name="configuration_programmatic", description="Programmatic Configuration", &>
<p>This section illustrates how to link the Myghty interpreter to a Python application.  If you already have a basic configuration running and want to jump into programming templates, skip ahead to <& formatting.myt:link, path="embedding" &>.</p>

<p>The central request-handling unit within Myghty is called the <b>Interpreter</b>.  When an application is set up to handle a request and pass control onto the Interpreter, it is referred to as an <b>external controller</b>.  In the model-view-controller paradigm, the application is the controller, the template called by the Interpreter is the view, and whatever data is passed from the controller to the template is the model.</p>

<p>Currently, all Myghty installations, except for mod_python, require at least a rudimentary external controller, which  serves as the place for configuration directives to be set up and specified to the Myghty environment.  Since a lot of configuration directives reference datastructures or functions themselves, a Python module is the most natural place for this to happen.</p>

<p>A more elaborate external controller may be the point at which an application passes control from its application code and business logic onto a view layer, served by a Myghty Interpreter and corresponding template files.  This may be appropriate for an application that is already handling the details of its HTTP environment, if any, or any application that just needs basic template support.</p>

<p>In contrast to the "external controller" concept is the <b>internal controller</b>, which is Python code that executes after the Interpreter begins handling the request, forwarding data onto template-driven components at the end of its request cycle.  Myghty provides a construct for this kind of controller described in <& formatting.myt:link, path="modulecomponents" &>.  It is recommended that an application that aims to be designed in a full MVC (model-view-controller) style, particularly one that runs in an HTTP environment, place its controller code into Module Components, and only application configuration code and externally-dependent code into a single external controller module.  That way the majority of an application's controller code is written in an environment-neutral fashion, and also has the full benefits of the Myghty resolution and request environment available to it.</p>

<p>The two general categories of external controller are:</p>
<ul>
	<li><& formatting.myt:link, path="configuration_programmatic_httphandler" &></li>
	<li><& formatting.myt:link, path="configuration_programmatic_interpreter" &></li>
</ul>

<&|doclib.myt:item, name="httphandler", description="Chaining to HTTPHandler", &>
<p>For applications running in an HTTP environment, chaining to HTTPHandler is the usual method.  An HTTPHandler object has awareness of HTTP requests for any of four different environments, which are WSGI, CGI, mod_python, and the standalone handler.  It can construct the appropriate HTTP-aware environment to be delivered to the Interpreter and ultimately onto templates, which then receive an implementation-neutral interface to that environment via the <i>r</i> global object.</p>

<p>All HTTP-based Myghty configurations utilize a subclass of <span class="codeline">myghty.http.HTTPHandler.HTTPHandler</span> to serve requests.  Each HTTP environment has its own module: <span class="codeline">myghty.http.ApacheHandler</span>, <span class="codeline">myghty.http.CGIHandler</span>, <span class="codeline">myghty.http.HTTPServerHandler</span> and <span class="codeline">myghty.http.WSGIHandler</span>, containing the classes <span class="codeline">ApacheHandler</span>, <span class="codeline">CGIHandler</span>, <span class="codeline">HSHandler</span>, and <span class="codeline">WSGIHandler</span>, respectively.</p>

<p>As of version 0.98, the recommended way to chain to an HTTPHandler is to first get an instance to a handler via the function <span class="codeline">get_handler()</span>, and then execute a request on that handler via the method <span class="codeline">handle()</span>.   In previous versions, a single function <span class="codeline">handle()</span> is used which combines the argument sets of both functions; this function is still available.</p>

<p>The get_handler function retrieves a handler from a registry based on the given <b>interpreter_name</b>, which defaults to 'main' or in the case of Apache uses the http.conf variable "MyghtyInterpreterName".  Application-scoped configuration variables are sent to this method which are used to create the initial HTTPHandler object.  Once created, subsequent calls with the same interpreter_name will return the same HTTPHandler instance.
</p>

<p>HTTPHandler then supplies the method <span class="codeline">handle()</span> to handle requests, which accepts configurational parameters on a per request basis.  Common per-request parameters include the component path or object to serve, the request arguments, and out_buffer to capture component output.</p>

<p>Each handler module has a slightly different calling signature, illustrated below.  </p>

<&|doclib.myt:item, name="ApacheHandler", description="ApacheHandler", &>
<p>The ApacheHandler handles mod_python requests.  It retrieves configuration via directives found in the host's httpd.conf file in the manner detailed in <&formatting.myt:link, path="configuration_mod_python"&>, and by default serves the component referenced by the <span class="codeline">request.uri</span> data member.  Configuration parameters sent programmatically override those found in the Apache configuration.</p>

<p>In the example below, a file "myghty_handler.py" is created, which contains a very simple mod_python handler that "chains" to the myghty ApacheHandler.</p>

<&|formatting.myt:code, syntaxtype="python", title="myghty_handler.py" &>
	import myghty.http.ApacheHandler as ApacheHandler
	from mod_python import apache

	def handle(request):
        handler = ApacheHandler.get_handler(request)
        return handler.handle(request)
</&>

<p>A configuration for the above file is similar to a straight Apache configuration.  Since the ApacheHandler created in the myghty_handler.py file contains no configuration at all, all of its options will come from the httpd.conf directives:</p>

    <&|formatting.myt:code, syntaxtype="conf" &>
       AddHandler mod_python .myt
       PythonHandler myghty_handler::handle
       PythonPath "sys.path+[r'/path/to/my/libraries']"
       PythonOption MyghtyComponentRoot r"/path/to/htdocs"
       PythonOption MyghtyDataDir r"/path/to/writeable/data/directory/"
    </&>

<p>When we take the above handler file and add configuration directives programmatically, they will override those named in the httpd.conf file:</p>

<&|formatting.myt:code, syntaxtype="python", title="myghty_handler.py" &>
	import myghty.http.ApacheHandler as ApacheHandler
	from mod_python import apache

	def handle(request):
        handler = ApacheHandler.get_handler(request,
                data_dir='/usr/local/web/data',
                component_root=[
                    {'components':'/usr/local/web/components'},
                    {'templates':'/usr/local/web/templates'}
                ])
        return handler.handle(request)
</&>

<P>Another example, overriding the application's data directory, and also the request's component path and request arguments:</p>
<&|formatting.myt:code, syntaxtype="python" &>
	import myghty.http.ApacheHandler as ApacheHandler
	from mod_python import apache

	def handle(request):
        handler = ApacheHandler.get_handler(
            request, interpreter_name = 'mainhandler', data_dir = '/data'
        )
        return handler.handle(request, 
            component = 'mypage.myt', request_args = {'foo' : 'bar'}
        )
</&>
<p>The above example also specifies the <&formatting.myt:link, path="parameters", param="interpreter_name"&> configuration parameter which identifies which ApacheHandler is returned by <span class="codeline">get_handler</span>.  If this parameter is not specified, it defaults to "main".</p>
</&>

<&|doclib.myt:item, name="CGIHandler", description="CGIHandler", &>
<p>The CGI handler retreives its environment information via the <span class="codeline">cgi.FieldStorage()</span> method as well as <span class="codeline">os.environ</span>.  Configuration parameters sent programmatically override those found in the CGI environment.  By default, CGIHandler serves the component indicated by the environment variable PATH_INFO.
</p>  

<&|formatting.myt:code, syntaxtype="python", title="CGI application chaining to CGIHandler.handle() function" &>
	#!/usr/local/bin/python

	import myghty.http.CGIHandler as CGIHandler

    # serve the component based on PATH_INFO
    CGIHandler.get_handler(
            component_root='/path/to/htdocs',
            data_dir='/path/to/datadirectory'
    ).handle()
</&>


</&>

<&|doclib.myt:item, name="WSGIHandler", description="WSGIHandler", &>
<p>WSGIHandler works similarly to CGIHandler.  Its <i>r</i> object maintains a reference to both the <&|formatting.myt:codeline&>environ</&> and <&|formatting.myt:codeline&>start_response</&> members.  These members are used to extract the core data members of the <i>r</i> object, such as <&|formatting.myt:codeline&>headers_in</&>, <&|formatting.myt:codeline&>method</&>, etc.  </p>

<p>When running under WSGI, the <span class="codeline">environ</span> and <span class="codeline">start_response</span> variables are available via:
<&|formatting.myt:code, syntaxtype="python"&>
	# WSGI environment variables

	r.environ
	r.start_response
</&>	
</p> 

<&|formatting.myt:code, syntaxtype="python", title="WSGI application chaining to WSGIHandler.handle() method" &>
	import myghty.http.WSGIHandler as WSGIHandler

	def application(environ, start_response):
		return WSGIHandler.get_handler(
			component_root='/path/to/htdocs', 
			data_dir='/path/to/datadirectory').handle(environ, start_response)	
</&>

<p>Also supported with WSGI is the standard <span class="codeline">application(environ, start_response)</span> function, which takes in all application and request-scoped configuration parameters via the <span class="codeline">environ</span> argument:</p>
<&|formatting.myt:code, syntaxtype="python", title="WSGI application via application()" &>
	import myghty.http.WSGIHandler as WSGIHandler

	params = dict(
	    interpreter_name='main_wsgi',
		component_root='/path/to/htdocs', 
		data_dir='/path/to/datadirectory'
	)

	def application(environ, start_response):
	    environ['myghty.application'] = params
	    environ['myghty.request'] = {'component' : 'mycomponent.myt'}
        return WSGIHandler.application(environ, start_response)
</&>


</&>

</&>


<&|doclib.myt:item, name="interpreter", description="Chaining to Interpreter", &>

<p>The Myghty Interpreter object is the underlying engine that creates Myghty requests and executes them, supplying the necessary services each request needs.   The Interpreter can be programmatically instantiated with a full set of configuration parameters and used directly.</p>
<p>While the advantage of using an HTTPHandler in an application is that Myghty components are aware of HTTP-specific information, such as the mod_python request object, HTTP headers, the httpd.conf configuration, etc., an application can also bypass all this by chaining directly to the Interpreter, if templates do not need HTTP awareness and the configuration can be programatically specified.</p>

<&|formatting.myt:code, syntaxtype="python", title="mod_python handler chaining to Interpreter" &>
	import myghty.interp as interp
	from mod_python import apache

	# set up a singleton instance of Interpreter
	interpreter = interp.Interpreter(
			data_dir = './cache',
			component_root = './doc/components',
		)

	def handle(request):
		# set up some data to send to the template
		data = {
			'foo': 'bar',
			'info' : get_info()
		}

		# call a template
		interpreter.execute('mytemplate.myt', request_args = data, out_buffer = request)

</&>

<p>In the above approach, Myghty components are unaware of the HTTP environment, meaning there is no <i>r</i> global variable, and also can't make HTTP return calls or location redirects.  A greater amount of responsibility is placed within the controller.</p>

<&|doclib.myt:item, name="standalone", description="Configuring a Standalone Application", &>
<p>Chaining to the Interpreter directly also allows Myghty to run outside of a web context completely, within any Python application.  It doesnt really need much configuration to run in "barebones" mode; the two most common features are the component root, which specifies one or more roots to search for input files, and the optional data directory, where it will store compiled python modules.  Without the data directory, the compiled python modules are created in memory only.</p>
<p>A standlone application to run Myghty templates looks like this:</p>

<&|formatting.myt:code, syntaxtype="python" &>
	#!/usr/local/bin/python

	import myghty.interp as interp
	import sys

	interpreter = interp.Interpreter(
			data_dir = './cache',
			component_root = './doc/components',
			out_buffer = sys.stdout
		)

	# component name is relative to component_root
	interpreter.execute('/index.myt')
</&>

<p>The <&|formatting.myt:codeline&>execute</&> method of Intepreter takes optional parameters and sends them off to a newly created <&|formatting.myt:codeline&>Request</&> object.  You can specify any of the constructor arguments used by <&|formatting.myt:codeline&>Request</&> or its embedded helper object <&|formatting.myt:codeline&>RequestImpl</&> in the <&|formatting.myt:codeline&>execute</&> call of Interpreter, which will override the values given in the constructor to Interpreter.  The below example sends a buffer to each request with which to capture output, via the <&formatting.myt:link, path="parameters", param="out_buffer" &> parameter:</p>

<&|formatting.myt:code, syntaxtype="python" &>
# write .myt file to a corresponding .html file
file = open('index.html', 'w')
interpreter.execute('/index.myt', out_buffer = file)
file.close()
</&>

</&>	

</&>


</&>	

