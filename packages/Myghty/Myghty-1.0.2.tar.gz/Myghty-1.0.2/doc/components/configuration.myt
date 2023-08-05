<%flags>inherit='document_base.myt'</%flags>

<&|doclib.myt:item, name="configuration", description="Configuration", &>
    <p>Below are configuration instructions for the three most basic types of configuration: the standalone handler, a CGI handler, and running under mod_python.  For further information on configuration, see:
    <ul>
        <li><a href="http://www.myghty.org/trac/wiki/How-to%27s_Configuration">How-to's_Configuration</a> - User-contributed configuration information at www.myghty.org, including:
            <ul>
                <li><a href="http://www.myghty.org/trac/wiki/How_to_Configure_lighttpd_%2B_mod_fastcgi_%2B_Myghty">How to Configure lighttpd + mod fastcgi + Myghty</a> - A configuration that one user acheives six times faster performance than an equivalent Apache configuration.
            </ul>
        </li>

        <li><&formatting.myt:link, path="parameters" &> - full index of configuration parameters</li>
        <li><&formatting.myt:link, path="configuration_programmatic" &> - writing Python modules that interface to Myghty in various ways</li>
        <li><&formatting.myt:link, path="resolver" &> - developing custom rulesets to match URIs to components</li>
        <li><&formatting.myt:link, path="caching_options" &> - configuring component-caching support</li>
        <li><&formatting.myt:link, path="session_options" &> - configuring session-storage support</li>
    </ul>
    
    </p>


    <&|doclib.myt:item, name="standalone", description="Standalone Handler", &>
    <p>The standalone handler is a web server built off of Python's BaseHTTPServer class, and is great for local workstation development and testing.  Here is a quick example to simply serve pages from the current directory - place the following code into a file <span class="codeline">run_server.py</span>:</p>

    <&|formatting.myt:code, syntaxtype="python"&>
    #!/usr/local/bin/python
    
    import myghty.http.HTTPServerHandler as HTTPServerHandler
    
    # create the server.
    httpd = HTTPServerHandler.HTTPServer(
        # port number to listen on.
        port = 8080,
        
        # HSHandler list.  indicates paths where the file should be interpreted
        # as a Myghty component request.
        # Format is a list of dictionaries, each maps a regular expression  matching a URI
        # to an instance of HTTPServerHandler.HSHandler, containing the arguments for
        # a Myghty interprter.  for HTTP requests of type "text/*", this list is matched
        # first against the incoming request URI.  
        handlers = [
            {'.*\.myt' : HTTPServerHandler.HSHandler(data_dir = './cache', component_root = './')},
        ],

        # document root list.  indicates paths where the file should be served
        # like a normal file, with the appropriate MIME type set as the content-type.
        # These are served for all non "text/*" HTTP requests, and all
        # incoming URIs that do not match the list of handlers above.
        docroot = [{'.*' : './'}],
        
    )       
            
    # run the server
    httpd.serve_forever()
    </&>
    <p>Then, in that same directory, place another file, called <span class="codeline">index.myt</span>:</p>

    <&|formatting.myt:code, syntaxtype="myghty"&>
    <html>
    <head><title>Test Page</title></head>
    <body>
        Welcome to Myghty !
    </body>
    </html>
    </&>
    <p>To run the server, type:</p>
    <&|formatting.myt:code, syntaxtype=None&>
        python ./run_server.py
    </&>
    
    <p>and point a web browser to <span class="codeline">http://localhost:8080/index.myt</span>.  The data directory <span class="codeline">./cache</span> will be automatically created to store data files.</p>
    
    
    
    <p>Other examples of the Standalone handler are available in <span class="codeline">examples/shoppingcart/run_cart.py</span> for a straightforward example, or <span class="codeline">tools/run_docs.py</span> for an advanced example that also makes use of custom resolution strategies.</p>
    </&>


    <&|doclib.myt:item, name="cgi", description="CGI", &>
    <p>Serving Myghty template files directly via CGI can be achieved with the <&|formatting.myt:codeline&>myghty.cgi</&> utility located in the <&|formatting.myt:codeline&>/tools</&> directory.  This program is a simple interface to the <&|formatting.myt:codeline&>CGIHandler</&>, which converts the "path-info" of the requested URI into a Myghty component call.  The script's configuration information is present within the top half of the script itself, to allow the most straightforward configuration, although it could certainly be modified to load configuration information from any other source such as other Python modules or configuration files.</p>
    
    <p>It requires configuration of the component root, data directory, and optionally additional Python libraries to run.  Other configuration parameters can be added to the <span class="codeline">handle()</span> call as well.  The cgi handler will handle requests of the form:<br/><br/>
    <&|formatting.myt:codeline&><% "http://<domain>/<cgi-bin directory>/myghty.cgi/<uri of template>"|h %></&>.
    </p>
    <p>The script is below.  Modify the appropriate lines and copy the myghty.cgi program into your webserver's cgi-bin directory for a basic cgi-based template handler.  For usage within custom CGI scripts, see the next section detailing programmatic methods of calling Myghty.</p>
    
    <&|formatting.myt:code, syntaxtype="python" &>
    #!/usr/local/bin/python
    
    # myghty cgi runner.  place in cgi-bin directory and address Myghty templates
    # with URLs in the form:
    
    # http://mysite.com/cgi-bin/myghty.cgi/path/to/template.myt
    
    # component root.  this is where the Myghty templates are.
    component_root = '/path/to/croot'
    
    # data directory.  this is where Myghty puts its object files.
    data_dir = '/path/to/datadir'
    
    # libraries.  Put paths to additional custom Python libraries here.
    lib = ['/path/to/custom/libraries']
    
    import sys
    [sys.path.append(path) for path in lib]
    
    import myghty.http.CGIHandler as handler
    
    handler.handle(component_root=component_root, data_dir=data_dir)
    </&>    
    

    </&>    



    <&|doclib.myt:item, name="mod_python", description="mod_python", &>
    
    <p>This section assumes familiarity with basic Apache configuration.  Myghty includes a handler known as <span class="codeline">myghty.http.ApacheHandler</span> which can interpret requests from the mod_python request object.  This handler can be configured directly within the httpd.conf file of Apache, using regular Apache configuration file directives to configure its options.  Alternatively, the ApacheHandler can be used within an external Python module that defines its own mod_python handler, which allows most of the configuration of the handler to be stated within a Python file instead of the httpd.conf file.  The first method, described in this section, is expedient for a straightforward Myghty template service, or a simple view-controller setup.  While the full range of configurational options can be present directly in http.conf stated as Apache configuration directives, including Python imports, functions, and datastructures, the syntax of embedding Python into conf directives can quickly become burdensome when configuring an application with a complex resolution stream.  Therefore it is recommended that Apache users also become familiar with programmatic configuration, described in the section <&formatting.myt:link, path="configuration_programmatic_httphandler_ApacheHandler"&>.</p>
    
<p>Myghty configuration parameters are written in the Apache httpd.conf file as "Myghty" plus the parameter name in InitialCaps.  The full range of configuration parameters in <&formatting.myt:link, path="params" &> may be used.  The values (right-hand side of the configuration directive) are Python evaluable expressions.  In the simplest case, this is just a string, which is mostly easily identified as <span class="codeline"><% 'r"<string>"' |h%></span> so that Apache does not strip the quotes out.  Any Python structure can be used as the value, such as a list, dictionary, lambda, etc., as long as the proper Apache conf escaping is used.</p>
    
<p>Below is a straightforward example that routes all Apache requests for files with the extension ".myt" to the Myghty ApacheHandler:</p>
    
    <&|formatting.myt:code, syntaxtype="conf" &>
    # associate .myt files with mod_python
    # mod_python 3.1 uses 'mod_python'
    AddHandler mod_python .myt

    # or for mod_python 2.7 use 'python-program'
    # AddHandler python-program .myt
    
    # set the handler called by mod_python to be the Myghty ApacheHandler
    PythonHandler myghty.ApacheHandler::handle

    # set python library paths - this line is used to indicate
    # additional user-defined library paths.  this path is not required for the 
    # Myghty templates themselves.
    PythonPath "sys.path+[r'/path/to/my/libraries']"

    # set component root.
    # for this example, an incoming URL of http://mysite.com/files/myfile.myt 
    # will be resolved as: /path/to/htdocs/files/myfile.myt
    PythonOption MyghtyComponentRoot r"/path/to/htdocs"

    # data directory where myghty will write its object files,
    # as well as session, cache, and lock files
    PythonOption MyghtyDataDir r"/path/to/writeable/data/directory/"

    # other options - simply write as 'Myghty' with the param name in
    # InitialCaps format, values should be legal python expressions
    # watch out for using quotes "" as apache.conf removes them - 
    # use r"value" or '"value"' instead
    PythonOption Myghty<paramname> <paramvalue>
        </&>

    <p>When this is done, requests to Apache which refer to pages with the extension .myt will be routed to the ApacheHandler, which will resolve the filename into a component which is then executed.</p>
    
    <p>An additional format for the "MyghtyComponentRoot" parameter, a list of multiple paths, can be specified as a list of dictionaries.  An example:
    <&|formatting.myt:code, syntaxtype="conf"&>
    # Multiple Roots, each has a key to identify it,
    # and their ordering determines their precedence
    PythonOption MyghtyComponentRoot <% "\\" %>
        "[  <% "\\" %>
             {'components':'/optional/path/to/components'}, <% "\\" %>
             {'main':'/path/to/htdocs/htdocs'} <% "\\" %>
        ]"
    </&>
    <p>
    Keep in mind that the MyghtyComponentRoot parameter (normally called component_root) defines filesystem paths that have no relationship to Apache DocumentRoots.  From the perspective of Apache, there is only a single mod_python handler being invoked, and it has no awareness of the component_root.  This means that any incoming URL which matches the Myghty handler will be matched to a root in the component_root and served as a Myghty template, effectively allowing "access" to files that are not directly access-controlled by Apache.  To restrict direct access to Myghty component files which are meant for internal use, an alternate file extension, such as ".myc" can be used, so that while a Myghty component can internally find those files within the component_root, the Apache server has no knowledge of the .myc extension and they are not served.  This also requires that the .myc files are kept in a directory or directories separate from any configured Apache DocuementRoots.</p>

    <p>
    Myghty also has the ability to handle directory requests and requests for nonexistent files via various mechanisms, including <&formatting.myt:link, path="specialtempl_dhandler"&> and <&formatting.myt:link, path="modulecomponents"&>.   However, the example above is configured to only respond to URLs with the specific file extension of ".myt".  To handle directory requests without a filename being present, or requests for many different file extensions at once, replace the usage of <&|formatting.myt:codeline&>AddHandler</&> with the Apache <&|formatting.myt:codeline&>SetHandler</&> directive combined with the <% "<FilesMatch>" |h%>, <% "<LocationMatch>" |h%>, or <% "<DirectoryMatch>" | h%> Apache directives.  These directives are described in the Apache documentation.  For example:
    </p>
    <&|formatting.myt:code, syntaxtype="conf"&><%text>
    <LocationMatch '/store/.*'>
        SetHandler mod_python
        PythonHandler myghty.ApacheHandler::handle
        PythonPath "sys.path+[r'/path/to/my/libraries']"
        
        # module component directive.  matches regular expressions to Python classes and functions.
        PythonOption MyghtyModuleComponents "[ \
                {'/store/product/.*':store:ProductHandler},\
                {'/store/checkout/.*':store:CheckoutHandler},\
            ]"
        PythonOption MyghtyComponentRoot r"/path/to/htdocs"
        PythonOption MyghtyDataDir r"/path/to/writeable/data/directory/"
    </LocationMatch>
    </%text></&>
    <p>The above MyghtyModuleComponents, the apache version of <&formatting.myt:link, path="parameters", param="module_components"&>, is just one way to serve module components; there is also <&formatting.myt:link, path="parameters", param="module_root"&>, as well as the Routes resolver.</p>
    
    <p>When serving all files within a directory, one should take care that Myghty is not be used to handle binary files, such as images.  Also, it might be inappropriate to serve other kinds of text files such as stylesheets (.css files) and javascript files (.js files), even though one could use Myghty templating to serve these.  To get around these issues, when straight file-extension matching is not enough, the Myghty and non-Myghty files can be placed in different directories and Apache correspondingly configured to enable Python handling in the Myghty directory only.
    </p>

    <&|doclib.myt:item, name="multiple", description="Advanced mod_python Configuration - Multiple ApacheHandlers", &>
    <p>Several Interpreters can be configured with their own set of configuration parameters and executed all within the same Python interpreter instance, through the use of the <&formatting.myt:link, path="parameters", param="interpreter_name"&> configuration parameter.
    
    In the example below, a site configures three main dynamic areas: a documentation section, a catalog section, and the default section for all requests that do not correspond to the previous two.  It uses three ApacheHandlers each with different component_root configuration parameters, but they share a common data_dir.  The handlers are each configured inside a <% "<LocationMatch>" | h %> directive where they are given a unique name that identifies them upon each request.</p>
    
    <&|formatting.myt:code, syntaxtype="conf"&><%text>
        # Apache resolves the LocationMatch directives in the order they 
        # appear so the most general directive is last.

        # note that every path within each "component root" parameter has a unique name, since 
        # all the Myghty interpreters happen to be using the same data directory.
        
        # also, the PythonPath is set for each SetHandler.  while this should work as a single
        # configuration for all three sections, in testing it seems to work sporadically, so its 
        # set explicitly for each one.

        # set Myghty data dir, will be used by all sub-directives
        PythonOption MyghtyDataDir r"/web/myapp/cache/"
        
        # '/docs/', serves product documentation
        <LocationMatch "/docs/.*\.myt">
            # set myghty handler
            SetHandler mod_python
            PythonHandler myghty.ApacheHandler::handle
            PythonPath "['/foo/bar/lib', '/usr/local/myapp/lib'] + sys.path"

            # set interpreter name
            PythonOption MyghtyInterpreterName r"document_interp"
            
            # set component root
            PythonOption MyghtyComponentRoot "[\
                {'docs_components' : r'/web/myapp/components'},\
                {'docs_htdocs' : r'/web/myapp/documents'},\
                ]"

            # add a translation rule to trim off the /docs/
            # when resolving the component
            PythonOption MyghtyPathTranslate "[\
                    (r'/docs/(.*)' : r'\1'),\
                ]"
        </LocationMatch>

        # '/catalog/', serves a browseable catalog via a module component
        # users can also log in to this area
        <LocationMatch "/catalog/.*">
            # set myghty handler
            SetHandler mod_python
            PythonHandler myghty.ApacheHandler::handle
            PythonPath "['/foo/bar/lib', '/usr/local/myapp/lib'] + sys.path"

            # set interpreter name
            PythonOption MyghtyInterpreterName r"catalog_interp"

            # set component root
            PythonOption MyghtyComponentRoot "[\
                    {'catalog_components' : r'/web/myapp/catalog/comp'},\
                ]"

            # configure some module components
            PythonOption MyghtyModuleComponents "[\
                    {r'/catalog/login' : 'myapp.components:Login'},\
                    {r'/catalog/.*' : 'myapp.components:Catalog'},\
                ]"
        </LocationMatch>

        # default: all other site docs
        <LocationMatch ".*\.myt">
            # set myghty handler
            SetHandler mod_python
            PythonHandler myghty.ApacheHandler::handle
            PythonPath "['/foo/bar/lib', '/usr/local/myapp/lib'] + sys.path"
                
            PythonOption MyghtyInterpreterName r"default_interp"
                
            # set component root
            PythonOption MyghtyComponentRoot "[\
                    {'default' : r'/web/myapp/htdocs'},\
                ]"
        </LocationMatch>
        

    </%text></&>
    
    <p>Configuring component roots and path translation based on the incoming URI can also be accomplished within the scope of a single Interpreter by defining a custom set of resolver rules.  This technique is described in <& formatting.myt:link, path="resolver" &>.</p>
    
    </&>

    </&>
</&>

