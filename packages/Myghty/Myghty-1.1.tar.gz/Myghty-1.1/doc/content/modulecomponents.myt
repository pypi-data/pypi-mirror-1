<%flags>inherit='document_base.myt'</%flags>

<&|doclib.myt:item, name="modulecomponents", description="Module Components", &>
<P>Module components build upon the component concept as introduced and explained in the previous section, <&formatting.myt:link, path="components"&>.  They represent a way of writing Myghty components using regular Python code within importable .py modules.  A module component can be used to handle requests, controlling the flow of an application across one or more templates; this role is known as a "controller".  Module components can also be embedded as component calls within templates just like any other component.   In both cases, Module Components are the appropriate place to place code-intensive control or view logic.</p>

<p>Module Components, or MC's, are not a new idea, and have analogies in other environments, such as the Java Servlet class, the mod_python handler() function, or the WSGI application() callable.  To suit the preferences of the both the class-oriented and the function-oriented developer, MC's can be written either as classes that subclass a specific Myghty class (similar to subclassing the Java Servlet class) or just as a regular Python function or callable object (i.e., an object instance that has a __call__ method).  Additionally, individual methods upon a class instance can also be called as MC's.  </p>

<p>When a plain Python function, callable object, or arbitrary instance method (herein will be generically referred to as a "callable") is to be called as a Module Component, the resulting component is referred to as an <b>implicit</b> module component.  In this case, the Myghty Interpreter is given the location of the callable either via a string pattern or via passing the callable itself, and is told to execute it as a component.  The Interpreter then creates a "real" component behind the scenes which <i>proxies</i> the Myghty argument set to the callable.  The developer need not be aware of this proxying component (though it is available).
</p>

<p>The flipside to the implicit module component is the <b>explicit</b> module component.  Here, the developer creates a class that is a subclass of <span class="codeline">myghty.component.ModuleComponent</span>, and implements the method <span class="codeline">do_run_component()</span>, which satisfies the execution of the component.  Like the implicit module component, the Interpreter is given its location either via a string pattern or via the Class object itself, and is told to execute it.  The Interpreter, upon receiving a Class object, instantiates the class which becomes directly the component to be executed; no "proxy" component is created.
</p>

<p>The differences between implicit and explicit module components are mostly differences in style.  The explicit form allows the developer more direct access to the flags, attributes, and argument lists of the component to be called, whereas the implicit form is more sparse, lightweight and flexible.  Both styles can be mixed; essentially, the Intepreter receives the object and determines the calling style based on the type of object passed to it.   In all cases, the rest of a Myghty application sees just more <span class="codeline">myghty.component.Component</span> objects, which have the same properties as any other component.
</p>

<p>An added layer of complexity to module components involves the configuration of URI resolution, which allows the mapping of arbitrary URI's to specific module component callables or classes based on different schemes.  This is required for MC's that are to be called as the top-level, request-handling component.  Myghty currently includes two methods of achieving this, which are described later in this section, as well as an API to allow any user-defined mapping algorithm (part of <&formatting.myt:link, path="resolver" &>).</p>


<&|doclib.myt:item, name="example", description="Example Module Component", &>
<p>Lets start with hello world.  All we need to do is create a new .py file, called <span class="codeline">hello.py</span>, and place the following function inside it:</p>

<&|formatting.myt:code, syntaxtype='python' &>
    def helloworld(m):
        m.write("hello world !")
</&>

<p>That is the extent of the module component itself.  Since it is a plain function, this is an "implicit" module component.</p>

<p>To call the component, the request object is given a string starting with the prefix "MODULE:", followed by the module name and name of the callable or class, separated by a colon.  In a template it is one of the following:</p>

<&|formatting.myt:code, syntaxtype='myghty' &><%text>
    # inline
    <& MODULE:hello:helloworld &>

    # code
    <%python>
        m.comp("MODULE:hello:helloworld")
    </%python>
</%text></&>

<p>Alternatively (release 0.99b), the "MODULE:" prefix can also be an "at" sign as follows:</p>
<&|formatting.myt:code, syntaxtype='myghty' &><%text>
    <& @hello:helloworld &>

    <%python>
        m.comp("@hello:helloworld")
    </%python>
</%text></&>
<p>
Both the module name and the callable/class name can contain any number of periods to represent sub-modules or sub-properties of the module.  Suppose <span class="codeline">helloworld</span> was a property on an object:
</p>

<&|formatting.myt:code, syntaxtype='python' &>
    hello = object()
    
    def doit(m):
        m.write("hello world !")
        
    hello.helloworld = doit
</&>

<p>This component can be called as:</p>
<&|formatting.myt:code, syntaxtype='myghty' &><%text>
    <& MODULE:hello:hello.helloworld &>
</%text></&>
<p>or just:</p>
<&|formatting.myt:code, syntaxtype='myghty' &><%text>
    <& @hello:hello.helloworld &>
</%text></&>


<p>The callable can have any argument list, and even the <i>m</i> variable is optional (though highly recommended).  Myghty uses the <span class="codeline">inspect</span> library to determine the desired arguments based on the callable's signature.  (for the performance minded, this is done only once when the component is first loaded).  Using the names present in the argument list, Myghty will determine which of the available global variables will be specified, as well as what required and optional component arguments this MC will require.  The component arguments are configured in exactly the same way as a template-based component configures its <% "<%ARGS>" | h %> section.</p>

<P>So to our "hello world" lets add the current and optionally tomorrow's weather:</p>

<&|formatting.myt:code, syntaxtype='python' &>
    def helloworld(m, today, tomorrow = None):
        m.write("hello world !  its a %s day today." % today)
        if tomorrow is None:
            m.write("Don't know what it is tomorrow, though.")
        else:
            m.write("But tomorrow, it'll be %s" % tomorrow)
</&>

<p>This component can be called like these examples:</p>

<&|formatting.myt:code, syntaxtype='myghty' &><%text>
    # inline shorthand
    <& @hello:helloworld, today='sunny' &>

    # inline longhand
    <& MODULE:hello:helloworld, today='sunny' &>

    # code
    <%python>
        m.comp("MODULE:hello:helloworld", today='cloudy', tomorrow='rainy')
    </%python>
</%text></&>


<p>The argument list of a module component may specify any of the standard and/or user-configured global arguments (globals were introduced in <& formatting.myt:link, path="globals" &>).  All arguments are passed by name, so the ordering is not important:
</p>

<&|formatting.myt:code, syntaxtype='python' &>
    def handle_request(m, ARGS, r, s, **params):
        # ...
</&>
<p>The above component specifies that it will receive the global variables <i>m</i>, <i>ARGS</i>, <i>r</i>, and <i>s</i>.  It also defines <span class="codeline">**params</span>, so all remaining component arguments will be in this dictionary.  A callable that defines simply <span class="codeline">**params</span> will receive <i>all</i> globals and component arguments within the dictionary.</p>
</&>
<&|doclib.myt:item, name="flavor", description="Flavors of Module Component", &>
<p>A summary of the various styles of MC are as follows.  For each of the below examples, assume the callable exists within a module named <span class="codeline">mylib.hello</span>:</p>

<&|doclib.myt:item, name="function", description="Function", &>
    This is the most basic type of implicit module component.
    <&|formatting.myt:code, syntaxtype='python' &>
        def helloworld(m, **params):
            m.write("hello world!")
    </&>
    
    Called as:
    
    <&|formatting.myt:code, syntaxtype='myghty' &><%text>
        <& MODULE:mylib.hello:helloworld &>
    </%text></&>
    
</&>

<&|doclib.myt:item, name="callable", description="Callable Object", &>
    <p>A callable object must be instantiated, but to the outside world looks almost the same as a function:</p>
    <&|formatting.myt:code, syntaxtype='python' &>
        class HelloWorld:
            def __call__(self, m, **params):
                m.write("hello world!")
        
        # instantiate the class
        helloworld = HelloWorld()
    </&>
    
    Called as:
    
    <&|formatting.myt:code, syntaxtype='myghty' &><%text>
        <& MODULE:mylib.hello:helloworld &>
    </%text></&>
    
    Note that this is identical to the previous function example.
    
</&>

<&|doclib.myt:item, name="method", description="Object Method", &>
    The object method is set up similarly to a callable object, the only difference being that a specific named method is called, instead of the generic <span class="codeline">__call__</span> method.  The difference lies in how it is specified when called.
    <&|formatting.myt:code, syntaxtype='python' &>
        class HelloWorld:
            def doit(self, m, **params):
                m.write("hello world!")
        
        # instantiate the class
        helloworld = HelloWorld()
    </&>
    
    Called as:
    
    <&|formatting.myt:code, syntaxtype='myghty' &><%text>
        <& MODULE:mylib.hello:helloworld.doit &>
    </%text></&>
    
    One particular quirk about the object method style is that if an object instance contains multiple methods that are called as MC's, the interpreter creates a <i>separate</i> "proxy" component for each method.</p>
    
    <p>With both callable object styles, the <i>same</i> object instance handles <i>many</i> requests, including multiple simultaneous requests among different threads, if the application is running in a threaded environment. A developer should take care to store request-scoped information as attributes upon the request object and <i>not</i> as instance variables of the object, as well as to appropriately synchronize access to instance variables and module attributes.
</&>

<&|doclib.myt:item, name="explicit", description="Class / Explicit Module Component", &>
    <p>This style works differently from the previously mentioned styles, in that the developer is writing a class directly against the Myghty API.  In this style, the developer directly defines the class of the component that is ultimately being accessed by the outside world.  No "proxying" component is created; instead, the Interpreter instantiates the specified class the first time it is referenced.  This also removes the need to explicitly instantiate the class:
    
    <&|formatting.myt:code, syntaxtype='python' &>
        import myghty.component
        
        class HelloWorld(myghty.component.ModuleComponent):
            
            def do_run_component(self, m, **params):
                m.write("hello world!")
        
    </&>
    
    Called as:
    
    <&|formatting.myt:code, syntaxtype='myghty' &><%text>
        <& MODULE:mylib.hello:HelloWorld &>
    </%text></&>
    
    <p>Note that the scoping rules for this style of component are the same, i.e. the same component instance is called for many requests and must be aware of variable scope as well as concurrency issues.</p>
    
    <p>The <span class="codeline">do_run_component</span> method works similarly to the callable of an implicit component.  Its argument list is dynamically inspected to determine the desired globals and component arguments, in the same way as that of implicit MC's.  However, there also is the option to bypass this inspection process and name the arguments explicitly, as well as their desired scope.  In previous versions of Myghty, this was the only way to define the arguments of an MC, but now its only optional.  This method is described in the next section, as well as the configuration of flags and attributes for MC's.
</&>


</&>


<&|doclib.myt:item, name="initialization", description="Module Component Initialization", &>

<p>Explicit MCs as well as implicit MCs based on an object instance have an optional initialization step that is called the first time the object instance is referenced. The method is called on an explicit ModuleComponent subclass as:
</p>
<span class="code">def do_component_init(self)</span>
<p>
And is called on an implicit callable object as:
</p>
<span class="code">def do_component_init(self, component)</span>

<p>In the second version, the argument <span class="codeline">component</span> is an instance of <span class="codeline">myghty.component.FunctionComponent</span> that is <b>hosting</b> the implicit module component's <span class="codeline">__call__</span> method or other method.   It is important to note that an object instance with many callable methods will actually have many FunctionComponents created, each one hosting an individual methods...<b>however</b>, the do_component_init() method is only called <b>once</b> with whatever FunctionComponent was first associated with the object.</p>

<p> In previous versions of Myghty, the initialization phase was required for components with arguments, which had to be explicitly declared within this stage.  As of version 0.98, explicit declaration of component arguments is optional, and the argument lists are by default determined from the signature of the explicit <span class="codeline">do_run_component</span> method or the implicit callable.</p>

<p>Explicit specification of an MCs arguments in the init section are as follows:</p>

<&|formatting.myt:code, syntaxtype='python'&><%text>
    import myghty.component as component
    
    class MyComponent(component.ModuleComponent):

        def do_component_init(self, **params):
            # component arguments
            self.args = ['arg1', 'arg2']
            
            # required component arguments
            self.required_args = ['arg3', 'arg4']
            
            # request-only arguments
            self.request_args = ['docid']
            
            # required request-only arguments
            self.required_request_args = ['userid']
            
            # subrequest or request arguments
            self.subrequest_args = ['foo']
            
            # required subrequest or request arguments
            self.required_subrequest_args = ['bar']
</%text></&>
<p>
A component as above would have the <span class="codeline">do_run_component</span> signature as follows:
</p>
<&|formatting.myt:code, syntaxtype='python'&><%text>
    def do_run_component(
        self, m, userid, arg3, arg4, bar, 
        docid = None, arg1 = None, arg2 = None, foo = None, **params
        ):
</%text></&>
<p>Note that if a module component defines any arguments explicitly in the do_component_init method, all arguments for the do_run_component method must be specified; no automatic introspection of function arguments will occur.</p>

<p>Similarly, <% "<%flags>" %> and <% "<%attr>" %> sections can be achieved like this:
</p>
<&|formatting.myt:code, syntaxtype='python'&><%text>
    def do_component_init(self, **params):
        # flags
        self.flags = {
            'autoflush':True,
            'trim': 'both'
        }
        
        # attributes
        self.attr = {
            'style':'green',
            'docid':5843
        }
        
</%text></&>
</&>


<&|doclib.myt:item, name="controller", description="Using MCs as Controllers", &>
<p>The two most prominent features of an MC used as a controller includes that URI resolution is configured so that one or more URIs result in the component being called directly from a request, and that the component typically uses subrequests to forward execution onto a template, which serves as the view.</p>

<p>Here are two versions of a controller component that is used to pull documents from a database based on the request arguments, and displays them via a template called "documents.myt".
</p>
<p><b>Figure 1: Implicit Style, using a Callable Object</b></p>
<&|formatting.myt:code, syntaxtype='python' &><%text>
    
    class DocumentManager:

        def do_component_init(self, component):
            # load some application-wide constants via Interpreter attributes.
            # the Interpreter is located via the hosting component.
            self.document_base = component.interpreter.attributes['document_base']
            self.db_string = component.interpreter.attributes['db_connect_string']

        def __call__(self, m, docid = None):

            # if no document id, return '404 - not found'       
            if docid is None:
                m.abort(404)

            # access a hypothetical document database
            docdb = get_doc_db(self.document_base, self.db_string)

            # load document
            document = docdb.find_document(docid)

            # couldnt find document - return '404 - not found'
            if document is None:
                m.abort(404)

            # run template
            m.subexec('documents.myt', document = document, **params)

    documentmanager = DocumentManager()

</%text></&>


<p><b>Figure 2: Explicit Style, with Pre-Declared Arguments</b></p>
<&|formatting.myt:code, syntaxtype='python' &><%text>
    import myghty.component as component
    
    class DocumentManager(component.ModuleComponent):

        def do_component_init(self, **params):
            # load some application-wide constants
            self.document_base = self.interpreter.attributes['document_base']
            self.db_string = self.interpreter.attributes['db_connect_string']

            # establish the argument names we want (optional as of 0.98)
            self.args = ['docid']

        def do_run_component(self, m, ARGS, docid = None, **params):

            # if no document id, return '404 - not found'       
            if docid is None:
                m.abort(404)

            # access a hypothetical document database
            docdb = get_doc_db(self.document_base, self.db_string)
            
            # load document
            document = docdb.find_document(docid)
            
            # couldnt find document - return '404 - not found'
            if document is None:
                m.abort(404)

            # run template
            m.subexec('documents.myt', document = document, **params)
            
</%text></&>
<p>
The next section describes the two methods of configuring request URIs to execute "controller" components like this one.
</p>
</&>

<&|doclib.myt:item, name="resolution", description="Configuring Module Component Resolution", &>
<p>
Module components can be used anywhere within the request, either right at the beginning (i.e. a controller) or within the scope of other components already executing.   A module component can be fetched and/or called based on its importable module name followed by a path to a callable object, or the name of a class that subclasses <span class="codeline">myghty.components.ModuleComponent</span>.  However, this doesn't work as a URL sent to a webserver. For request-level operation, MCs must be mapped to URIs.  This resolution is achieved through two different configuration directives, <span class="codeline">module_components</span> and <span class="codeline">module_root</span>.  A third option also exists which is to use the new <span class="codeline">routesresolver</span> resolver object.</p>

<&|doclib.myt:item, name="module_components", description="module_components", &>
The module_components configuration parameter looks like this:

<&|formatting.myt:code, syntaxtype="python" &>
    module_components = [
        {r'myapplication/home/.*' : 'myapp.home:HomeHandler'}, 
        {r'myapplication/login/.*' : 'myapp.login:LoginHandler'}, 
        {r'.*/cart' : 'myapp.cart:process_cart'}, 
        {r'.*' : 'myapp.home:HomeHandler'} 
    ]
</&>

Which in an apache configuration looks like:

<&|formatting.myt:code, syntaxtype="conf" &>
    PythonOption MyghtyModuleComponents "[ <% "\\" %>
        {r'myapplication/home/.*' : 'myapp.home:HomeHandler'}, <% "\\" %>
        {r'myapplication/login/.*' : 'myapp.login:LoginHandler'}, <% "\\" %>
        {r'.*/cart' : 'myapp.cart:ShoppingCart'}, <% "\\" %>
        {r'.*' : 'myapp.home:HomeHandler'} <% "\\" %>
    ]"
</&>

<p>
Each entry in the module_components array is a single-member hash containing a regular expression to be matched against the incoming URI, and an expression that can be resolved into a Module Component.  This expression can be any of the following forms:
</p>
<&|formatting.myt:code, syntaxtype="python" &>
    module_components = [
        # a string in the form '<modulename>:<classname>'           
        {r'myapplication/home/.*' : 'myapp.home:HomeHandler'}, 
        
        # a string in the form '<modulename>:<functionname>'
        {r'myapplication/login/.*' : 'myapp.login:do_login'}, 
        
        # a string in the form '<modulename>:<some>.<callable>.<thing>'
        {r'myapplication/status/.*' : 'myapp.status:handler.mcomp.get_status'},
        
        # a Class
        {r'.*/cart' : MyClass}, 
        
        # a function reference, or reference to a callable() object
        {r'.*/dostuff' : do_stuff},
        
        # reference to a class instance method
        {r'.*' : mymodule.processor.main_process}
    ]
</&>
<p>
Generally, its better to use the string forms since they encompass all the information needed to load the class or callable object, which allows the Myghty interpreter to dynamically reload the object when the underlying module has changed.
</p>

<p>For module components that resolve to a Class, the Class will be instantiated by the Interpreter, and is expected to be a subclass of <span class="codeline">myghty.component.ModuleComponent</span>.  This is also known as an <b>explicit</b> module component.  For components that resolve to a function, object instance method, or callable object (i.e. any object that has a __call__ method), a "wrapper" module component will be created automatically which adapts to the callable's argument list.  This is also known as an <b>implicit</b> module component.
</p>

<&|doclib.myt:item, name="additional", description="Passing Resolution Arguments", &>

<p>The module_components configuration parameter also includes some methods of returning information about the actual resolution of the component at request time.</p>

<p>Since module_components uses regular expressions to match URIs to components, the <span class="codeline">re.Match</span> object produced when a match occurs can be accessed via the <i>m</i> global variable.  This example places capturing parenthesis in the regular expression to capture the additional path information:</p>

<&|formatting.myt:code, syntaxtype="python",  &>
    module_components = [
        # place capturing parenthesis in the regexp
        {r'/catalog/(.*)' : 'store:Catalog'}
    ]
</&>

The contents of the capturing parenthesis are available as:

<&|formatting.myt:code, syntaxtype="python",  &>
    m.resolution.match.group(1)
</&>

<p>User-defined arguments can also be configured which will be passed to the request object at resolution time.  To use this form, a dictionary is used instead of a single string to specify the module and callable/class name of the component, and the address of the component itself is placed under the key 'component':</p>

<&|formatting.myt:code, syntaxtype="python",  &>
    module_components = [
        # supply the component with some arguments
        {r'/login/' : 
            {
            'component' : 'myapp:loginmanager',
            'ldap_server' : 'ldap://localhost:5678'
            }
        }
    ]
</&>

The contents of the <span class="codeline">ldap_server</span> argument are available as:

<&|formatting.myt:code, syntaxtype="python",  &>
    m.resolution.args['ldap_server']
</&>
</&>

<p>The corresponding Resolver class for module_components is ResolveModule.
</p>

</&>

<&|doclib.myt:item, name="module_root", description="module_root", &>
<p>This parameter locates module components based on paths.  It is similar to the <&formatting.myt:link, path="parameters", param="component_root" &> configuration parameter in that it defines one or more roots which will all be matched against the incoming URI.  However, it not only traverses through  directories, it also will traverse into a Python module where it attempts to locate a function or callable object instance.  Currently, only the "implicit" style of module components can be used with module_root (but module_components, from the previous section, can be used with implicit or explicit MCs).
</p>

<p>The entries in module_root take the following forms:</p>

<&|formatting.myt:code, syntaxtype="python",  &>
    module_root = [
        # a regular file path
        '/web/lib/modules/',
        
        # the full file path of a Python module
        '/web/extra/modules/mycontroller.py',
        
        # the name of an importable Python module
        'mylib.loginhandlers',
    ]
</&>

<p>Using the first path '/web/lib/modules', heres an example.  Start with the following file:</p>

<&|formatting.myt:code, syntaxtype=None,  &>
    /web/lib/modules/admin/login.py
</&>

<p>This file contains the following code:</p>

<&|formatting.myt:code, syntaxtype="python",  &>

    def hello(m):
        m.write("hello world!")
        
    class _do_login:
        def __call__(self, m):
            m.write("please login")
            # ....
    
        def foo(self, m):
            m.write("this is foo")
            
    index = _do_login()
    
    _my_var = 12
</&>

<p>Finally, lets have a module_root of:</p>

<&|formatting.myt:code, syntaxtype="python",  &>
    module_root = ['/web/lib/modules']
</&>

<p>With this configuration, URLs will be resolved as follows:</p>

<&|formatting.myt:code,  syntaxtype=None &>
    http://mysite.com/admin/login/hello/     --->  "hello world!"    (login.py:hello())
    http://mysite.com/admin/login/           --->  "please login"    (login.py:index.__call__())
    http://mysite.com/admin/login/foo/       --->  "this is foo"     (login.py:index.foo())
    http://mysite.com/admin/login/lala/      --->  "please login"    (login.py:index.__call__())
    http://mysite.com/admin/login/_my_var/   --->  "please login"    (_my_var is private and is skipped)
    http://mysite.com/admin/lala/            --->  404 not found     (no file named lala.py)
    
</&>
<p>The spirit of this resolver is that of the mod_python Publisher handler.   Path tokens are converted into the names of .py files on the filesystem.  When a file is located and it is a valid Python module, the module is loaded and further path tokens are resolved as attributes within the module itself.  Attributes that start with an underscore are skipped, which is the default way to flag "private" attributes.  There is also a "public" attribute marker which can be used to mark public functions instead of marking private functions, explained in the options section below.  If no matching attribute exists for a path token, it looks for the attribute name "index", else returns a ComponentNotFound exception.
</p>
<&|doclib.myt:item, name="options", description="Module Root Options", &>
<p>The underlying Resolver object for the module_root parameter is called ResolvePathModule (resolver objects are described in <&formatting.myt:link, path="resolver" &>).  This object also has configuration options of its own.  These options may be specified to the ResolvePathModule constructor directly.  They can be specified as regular Myghty configuration parameters as well as of version 0.99b:
    <ul>
        <li><p>module_root_adjust=None (release 0.99b) - a reference to a function which receives the incoming URI and returns a modified version of that URI with which to resolve.  The modified URI is not propigated onto other rules in the resolution chain, so therefore it represents a "local" alternative to <&formatting.myt:link, path="parameters", param="path_translate"&>.</p>
        <p>This parameter is also called 'adjust' in all releases, but that name conflicts with the same name in the ResolveFile resolver, so should only be used when constructing individual ResolvePathModule objects and not as a global configuration parameter.</p>
        </li>
        <li><p>require_publish=False - when set to True, the callable object must have an attribute <span class="codeline">publish</span> set to True in order to mark it as publically accessible; else it will not be resolved.  This effectively reverses the "negative publishing" model established via the underscore "_" syntax into a "positive publishing" model.  Given this configuration:</p>
        
        <&|formatting.myt:code, syntaxtype="python",  &>
            module_root = ['/web/lib/modules']
            require_publish = True
        </&>
        
<p>Marking functions and methods public looks like this:
    <&|formatting.myt:code, syntaxtype="python",  &>
        class MyController(object):
            def __call__(self, m, **kwargs):
                # ...
                m.subexec('mytemplate.myt')
            __call__.public = True
                
            def do_stuff(self, m, **kwargs):
                # ...
                m.subexec('dostuff.myt')
            do_stuff.public = True
            
        def call_index(m,r, s, ARGS):
            # ...
            m.subexec('index.myt')
        call_index.public = True
        
        mycallable = MyController()
    </&>    
    
<p>The public attribute can also be set in Python 2.4 via decorator:</p>
    <&|formatting.myt:code, syntaxtype="python",  &>
        def mark_public(func):
            func.public = True
            return func
            
        @mark_public
        def mycontroller(m, **kwargs):
            # ...
    </&>
        </li>
        <li>path_moduletokens=['index'] - this is a list of special "default" token names when searching for module attributes.  For example:  If a given path "/foo/bar/bat" resolves to the module "bar.py" inside of directory "foo/", it will first look for an attribute named "bat" inside the module.  If "bat" is not present, it will then look for all the names inside the moduletokens list, which defaults to the single entry "index".  Therefore /foo/bar/bat not only looks for "bat", it also looks for "index".  The tokens inside moduletokens are checked as defaults for every module token, so that a path such as "/foo/bar/bat" can also correspond to a module attribute "foo.index.bat", "index.bar.bat", etc.</li>
        <li>path_stringtokens=[] - this is the path equivalent to the moduletokens parameter.  It is a list of "default" path tokens when searching for files.  In some ways, this parameter's functionality overlaps that of <&formatting.myt:link, path="parameters", param="dhandler_name"&>, except it allows multiple names and applies only to the module_root configuration.  For example, if stringtokens is configured to ["default", "index"], and a given path "/foo/bar" resolves to the directory "foo/" but there is no file named "bar.py" inside the directory, it will then look for the files "default.py" and "index.py", respectively.  Like moduletokens, stringtokens also checks these defaults for every path token, so a URL of "/foo/bar/bat" can also match "/default/bar/index", for example.</li>
    </ul>
</&>
<p>module_root can also be combined with dhandler resolution (described in <&formatting.myt:link, path='specialtempl_dhandler' &>), so that a file named <span class="codeline">dhandler.py</span> in the current or parent directory serves as the "default" Python module for a path token that does not correspond to any other file.  In the case of ResolvePathModule locating a dhandler.py file, the additional path tokens that normally reside within <& formatting.myt:link, path="request_members", member="dhandler_path"&> are also searched as attributes within the dhandler.py module.
</p>

<p>The corresponding Resolver class for module_root is ResolvePathModule.
</p>
</&>
<&|doclib.myt:item, name="routesresolver", description="Routes Resolver", &>
<P>The Routes Resolver provides Rails-like functionality, building upon the resolution architecture described in <&formatting.myt:link, path="resolver"&>.  Since it is not part of the default set of resolver objects, it must be included in the resolution chain via the <&formatting.myt:link, path="parameters", param="resolver_strategy"&> configuration parameter.</p>

<p>A rudimentary example of the Routes resolver can be viewed by installing the <span class="codeline">myghty_routes</span> Paste template.  Instructions for installing Paste templates are in <& formatting.myt:link, path="installation_paste"&>.  The routes resolver also serves as the core resolver for the <a href="http://pylons.groovie.org">Pylons</a> web framework which is based on Myghty, and includes more comprehensive and up-to-date examples.
</p>
</&>

</&>


<&|doclib.myt:item, name="preprocessor", description="Module Component Pre and Post processing", &>

<p>Request-handling module components can also be used to perform pre- and post-processing on a request.  This means that the information about a request is modified before and/or after the main response is determined.  The following two examples both wrap the main body of the request inside of a subrequest.</p>

<p>A module component that performs translations on incoming URI's, and then passes control onto the requested template, looks like this:</p>

<&|formatting.myt:code, syntaxtype='python'&><%text>
    def translate_path(self, m, **params):
        path = m.get_request_path()
        path = re.sub('/sitedocs/john/', '/', path)
        m.subexec(path, **params)
    
</%text></&>
<p>A URI configuration for this component might look like:</p>

<&|formatting.myt:code, syntaxtype="python"&><%text>
    module_components = [{r'/sitedocs/john/.*\.myt', 'mymodule:translate_path'}]
</%text></&>

<p>Path translation is also accomplished in Myghty via the <&formatting.myt:link, path="parameters", param="path_translate"&> parameter, and can be controlled in finer detail through the use of custom resolution rules, described in <&formatting.myt:link, path="resolver" &>.</p>

<p>An example post processing component, which filters the output of the subrequest before returning data:
</p>

<&|formatting.myt:code, syntaxtype='python' &><%text>
    import StringIO, re
    
    def filter(self, m, **params):
        # make a buffer
        buf = StringIO.StringIO()

        # create a subrequest using that buffer
        # our templates are located relative to the 
        # request URI underneath '/components'
        subreq = m.create_subrequest('/components' + m.get_request_uri(), out_buffer = buf)

        # execute the subrequest
        ret = subreq.execute()

        # perform a meaningless filter operation on the content
        content = re.sub(r'foo', r'bar', buf.getvalue())            

        # write the content                 
        m.write(content)
          
</%text></&>
<p>This component might be configured as:</p>

<&|formatting.myt:code, syntaxtype="python"&><%text>
    module_components = [{r'/sitedocs/john/.*\.myt', 'mymodule:filter'}]
</%text></&>

<p>Filtering is also built in to Myghty via the use of <% "<%filter>" %> section, described in <& formatting.myt:link, path="filtering" &>.
</p>

</&>

<&|doclib.myt:item, name="templates", description="Using Module Components within Templates", &>
<p>MCs can also be called from within templates.  If an MC is configured to be callable against a URI using <span class="codeline">module_components</span> or <span class="codeline">module_root</span>, that URI can also be used within a regular <% "<& &>" | h %>-style component call.  Or, the MODULE: prefix style described previously can be used.</p>

<&|doclib.myt:item, name="formexample", description="Example: Form Visitor", &>
<p>Here is an example of a module component that is used to generate HTML forms from a data object, using the visitor pattern.  Such an architecture can be used to have form information stored in a database or XML file which can then be used to automatically construct a corresponding form.  This example is included in working form with the Myghty distribution.
</p>

<p><b>Step 1: Data Model</b> - The data model consists of a hierarchy of <span class="codeline">FormElement</span> objects.  Some <span class="codeline">FormElement</span> objects can contain collections of other <span class="codeline">FormElements</span> (the "composite" pattern):</p>
<&|formatting.myt:code, title='form.py', syntaxtype='python'&><%text>
    class FormElement(object):
        """ abstract FormElement superclass."""
        
        def __init__(self):
            pass
        
        def accept_visitor(self, visitor): 
            """subclasses override accept_visitor to provide
            the appropriate type-based visitor method."""
            pass
        
    class Form(FormElement):
        """represents a <FORM> tag."""

        def __init__(self, name, action, elements):
            self.name = name
            self.action = action
            self.elements = elements

        def accept_visitor(self, visitor):
            visitor.visit_form(self)
        
    class Field(FormElement):
        """abstract base class for individual user-entry fields, each 
        having a name, a description, and an optional value."""

        def __init__(self, name, description, value = None):
            self.name = name
            self.description = description
            self.value = value
        
    class TextField(Field):
        """an <INPUT TYPE="text"> field."""

        def __init__(self, name, description, size, value = None):
            Field.__init__(self, name, description, value)
            self.size = size

        def accept_visitor(self, visitor):
            visitor.visit_textfield(self)
            
    class SelectField(Field):
        """a <SELECT></SELECT> tag."""

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
        """an <OPTION></OPTION> tag.
        contains a parent attribute that points to a <SELECT> field."""

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

</%text></&>

<p><b>Step 2: Visitor Interface</b> - This class provides the layout of a visitor object:</p>
<&|formatting.myt:code, syntaxtype='python', title='form.py' &><%text>
    class FormVisitor:
        def visit_form(self, form):pass
        def visit_textfield(self, textfield):pass
        def visit_selectfield(self, selectfield):pass
        def visit_option(self, option):pass
        def visit_submit(self, submit):pass
</%text></&>

<p><b>Step 3: HTML Rendering Components</b> - a set of Myghty methods that will render the HTML of each form element:
</p>
<&|formatting.myt:code, title="formfields.myc"&><%text>
    <%doc>
        each method renders one particular HTML form element, 
        as well as <table> tags to provide basic layout for each.  
        the "form" and "select" methods are component calls with content, 
        to render the form elements within them.
    </%doc>
    
    <%method form>
        <%args>form</%args>
        
        <FORM name="<% form.name %>" method="POST" action="<% form.action %>">
        <table>
        <% m.content() %>
        </table>
        </FORM>
    </%method>
    
    <%method textfield>
        <%args>textfield</%args>

        <tr>
            <td><% textfield.description %>:</td>
        
            <td>
            <input type="text" name="<% textfield.name %>" value="<% textfield.value %>" size="<% textfield.size %>" >
            </td>
        </tr>
    </%method>
    
    <%method submit>
        <%args>submit</%args>
        
        <tr><td colspan="2">
            <input type="submit" value="<% submit.value %>">
        </td></tr>
    </%method>
    
    <%method select>
        <%args>select</%args>
        
        <tr>
            <td><% select.description %></td>
            <td>
                <select name="<% select.name %>">
                <% m.content() %>
                </select>
            </td>
        </tr>
    </%method>
    
    <%method option>
        <%args>option</%args>
        <option value="<% option.id %>" <% option.selected and "SELECTED" or "" %>><% option.description %></option>
    </%method>
</%text></&>

<p><b>Step 4: Module Component</b> - ties it all together.  The FormGenerator serves as the traversal unit for the Form object, as well as the visitor implementation itself.  The visit_form and visit_selectfield methods both involve contained formelements, and the corresponding myghty components are component calls with content; so for those, a content function is created to handle the embedded content.
</p>
<&|formatting.myt:code, syntaxtype='python', title='form.py'&><%text>

    def renderform(self, m, form, **params):
        form.accept_visitor(FormGenerator.RenderForm(m))
        
    class RenderForm(FormVisitor):
        def __init__(self, m):
            self.m = m

        def visit_form(self, form):
            def formcontent():
                for element in form.elements:
                    element.accept_visitor(self)

            self.m.execute_component("formfields.myc:form", args = dict(form = form), content=formcontent)

        def visit_textfield(self, textfield):
            self.m.comp("formfields.myc:textfield", textfield = textfield)

        def visit_selectfield(self, selectfield):
            def selectcontent():
                for element in selectfield.options:
                    element.accept_visitor(self)

            self.m.execute_component("formfields.myc:select", args = dict(select = selectfield), content=selectcontent)

        def visit_option(self, option):
            self.m.comp("formfields.myc:option", option = option)

        def visit_submit(self, submit):
            self.m.comp("formfields.myc:submit", submit = submit)

    
</%text></&>

<p><b>Step 5: Fire it Up</b> - this myghty template actually calls the <span class="codeline">renderform</span> Module Component.
</p>
<&|formatting.myt:code, title="registration.myt"&><%text>
    <%doc>
        an example firstname/lastname/occupation registration form.
    </%doc>
    
    <%python>
        import form
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
    
    Welcome to the Skydivers or Computer Programmers Club !
    
    <& MODULE:form:renderform, form = registerform &>
    
</%text></&>

</&>



</&>

</&>
