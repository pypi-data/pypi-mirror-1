<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="technical", description="Myghty Guts (tech description)", &>
    <p>This section refers to the inner workings of Myghty and how it relates to HTML::Mason.</p>

<&|doclib.myt:item, name="goals", description="Design Goals", &>
<p>The main goal in developing Myghty is, port HTML::Mason to Python !  Beyond that, it is important that it retain all the central features of HTML::Mason, to make it easy for people already familiar with Mason to use Myghty as well.  </p>


<p>But even though the language should be similar to Mason's, it also should be altered as needed to appropriately fit the Python language style, which while having some notable similarities to Perl, is still a different beast.   The design of the engine should model itself after that of Mason's at a high level, but also should take advantage of the opportunities the "clean start" porting to Python gives, including code streamlining, introduction of new design patterns, and putting to use the unique programming capabilities Python affords (since after all, I wouldnt be porting to Python if I didn't think Python had some unique things to offer).  </p>

<p>Going forward, the design and featureset of Myghty is expected to diverge from that of HTML::Mason, which is seen as more of a "starting point" rather than a continuous benchmark to follow.  Since it is intended for a different audience than that of Mason, i.e. the Python developmental community, I am hoping that its development can be steered into being a useful and "first choice" enterprise web development tool specifically for Python enthusiasts.
</p>
</&>

    <&|doclib.myt:item, name="templates", description="Approaches to Templating", &>

    <p>Myghty is a <b>compiled page</b> system, as opposed to a <b>directly interpreted</b> system.  A compiled page system means that templates are used to generate source code files consisting a programming language that is different from that of the actual template, typically the same language as that of the language compiler itself.  Whereas a directly interpreted language provides its own language interpreter for templates.  Compiled page systems include Java Server Pages, Embperl, HTML::Mason, Python Server Pages.  Directly interpreted systems include PHP, Webmacro, and FreeMarker (whose early development history bears the name of Myghty's author). </p>
    
    <p>Each approach has its own advantages and disadvantages.  A directly interpreted system has the burden of providing a full programming language written from scratch, which can result in a language that is somewhat rigid and single-purposed, but can potentially deliver extremely fast performance.   A compiled page system is much simpler to write, and typically allows full blocks of the host language to be dropped into templates.  This allows great flexibility, but is also known to result in templates that are more complicated than is appropriate, depending on the developer's code practices. 
 For developers of Python code, Python is probably an elegant and powerful enough language that it deserves to live within templates unadulterated, as it does within Myghty.</p>  
    </&>

    <&|doclib.myt:item, name="generation", description="Generating Python Modules", &>
    
    <p>A Myghty template file, which might have an extension such as ".myt", is parsed by the engine and converted into a python module, which contains a subclass of the class <span class="codeline">Component</span>.   This new python module, which also gets compiled by python into a .pyc file, then forms the basis for generating the template's final output, and is only changed whenever the original template changes.</p>
    
    <p>The majority of the template is encoded as Python statements inside of a class method called <span class="codeline">do_run_component()</span>.  Straight text from the template file gets distilled into <span class="codeline">write</span> statements, lines and blocks of Python code get inserted inline as they are (with their whitespace adjusted to the appropriate context), and calls to other parts of the template or other templates get translated into calls that look like <span class="codeline">m.execute_component()</span>.  
    A pre-determined namespace of one or more helper variables is provided to statements within the template so that your template can attend to its daily chores, such as looking at the apache request, sending headers, ordering takeout, what have you.  Other details to be dealt with by <span class="codeline">Component</span> include handling argument lists being passed around as well as properly specifying the scoping of variables and custom methods.</p>
    
    </&>

    <&|doclib.myt:item, name="request", description="Handling a Request", &>
    <p>
    A request starts first with the module that is handling the host environment.  This may be the ApacheHandler, the CGIHandler, a standalone handler, or any developer-custom handler (they're pretty easy to write).</p>

    <p>The handler then is responsible for creating an instance of <&|formatting.myt:codeline&>myghty.interp.Interpreter</&> with the proper arguments corresponding to the execution environment, and then calling the <&|formatting.myt:codeline&>execute()</&> method on that interpreter with request-specific arguments, which will begin the process of compiling, loading, and running a Myghty template.</p>

    <p>The Interpreter then creates an instance of <&|formatting.myt:codeline&>myghty.request.Request</&> which represents the template and arguments we are actually going to serve, and optionally a <&|formatting.myt:codeline&>myghty.request.RequestImpl</&> object which provides additional environment-specific behavior to the Request object, including the request arguments and the output buffer where content will be written.
    </p>

    <p>
    Request is responsible for looking up the requested component and also other referenced components, which may be inherit components, methods in other component files, etc.  The individual lookup operations are sent back to the hosting Interpreter object, which will coordinate amongst an instance of <&|formatting.myt:codeline&>myghty.resolver.Resolver</&> to locate files, a cache of <&|formatting.myt:codeline&>myghty.resolver.ComponentSource</&> instances representing located template files, and a thread-local instance of <&|formatting.myt:codeline&>myghty.compiler.Compiler</&> which is responsible for parsing in new template files and producing compiled component files from them, from which Interpreter can receive new <&|formatting.myt:codeline&>myghty.component.Component</&> objects.  <&|formatting.myt:codeline&>myghty.compiler.Compiler</&> makes use of the <&|formatting.myt:codeline&>Lexer</&> and <&|formatting.myt:codeline&>ObjectGenerator</&> objects to compile templates.
    </p>

    <p>
    The Request object executes the components it locates, passing itself as the primary namespace variable <i>m</i> to components, manages a call-stack of components, and manages a stack of <&|formatting.myt:codeline&>myghty.buffer.AbstractBuffer</&> objects which capture component output.  Exceptions are also handled here and processed so that they contain clean stack traces.</p>

    <p>Request then cleans up and finishes, Interpreter finishes, and its back up to the handler to send return codes and exit its handle method.
    </p>

    </&>

<&|doclib.myt:item, name="modules", description="Modules", &>
<p>To gain a deeper understanding of Myghty, heres a quick rundown of the modules and what their purpose is.</p>

    <&|doclib.myt:item, name="request", description="request", &>
    <p>The request package is home to the Request object.  Request is an object that is instantiated by Interpreter to service a top-level component exactly once.  It is available within a component's namespace by the special variable <i>m</i>.  It is responsible for locating all components and inherited components referenced by its top-level component, including autohandlers and dhandlers, calling them in the appropriate order, buffering their output, and handling exceptions.  It interacts with the outside world via an embedded RequestImpl object, such as DefaultRequestImpl (also included in the request package) for dealing with a command-line environment, ApacheRequestImpl for dealing with mod_python, and CGIRequestImpl which handles a CGI environment.
    </&>
    <&|doclib.myt:item, name="interp", description="interp", &>
    <p>interp is home to the Interpreter object.  Interpreter represents a Myghty application environment and its configuration parameters, and is the primary API used for executing requests within that environment.  Interpreter contains logic for loading and compiling component objects at a high level, and dispatching those compiled component objects to new requests.  It also deals with the filesystem structure where component files, lock files, and cache files are stored.</p>
    </&>
    <&|doclib.myt:item, name="lexer", description="lexer", &>
    <p>
    The lexer package contains the Lexer object, which is responsible for parsing component files or in-memory strings and sending the resulting tokens to an instance of Compiler.  Lexer relies heavily on the regular expression package to produce its results.
    </p>
    </&>
    <&|doclib.myt:item, name="compiler", description="compiler", &>
    <p>
    Compiler represents a location for Lexer to send its parsing events, and aggregates a compiled parse tree structure for a particular compilation.  Once complete it calls an instance of ObjectGenerator with the new parse tree to produce the source code of a Myghty component.  The parse tree itself is an instance of Compiler.Compiled, which stores the various code blocks and supports visitor-based traversal.
    </p>
    </&>
    <&|doclib.myt:item, name="objgen", description="objgen", &>
    <p>
    The home to ObjectGenerator, PythonGenerator, and PythonPrinter.  ObjectGenerator is a generic interface for receiving visitor events from a compiled structure.  The PythonGenerator extends ObjectGenerator to produce source code strings/files from that compiled structure.  PythonPrinter handles printing of python code lines while keeping track of the indentation level, to allow all kinds of Myghty blocks to aggregate into one coherent Python source file.
    </p>
    </&>
    <&|doclib.myt:item, name="component", description="component", &>
    <p>
    component contains the hierarchy of Component, FileComponent and SubComponent, which serve as the base classes for user-defined Myghty components.  FileComponent contains initialization logic for handling requestlocal and threadlocal sections, as well as the initial determination of inheritance.
    </p>
    </&>
    <&|doclib.myt:item, name="resolver", description="resolver", &>
    <p>
    contains the Resolver object and the various built in ResolverRule objects.  The Resolver
    is called by the Interpreter.
    </p>
    </&>
    <&|doclib.myt:item, name="escapes", description="escapes", &>
    <p>
    Contains code for handling substitution escaping, which includes URL, HTML and XML escaping.
    </p>
    </&>
    <&|doclib.myt:item, name="buffer", description="buffer", &>
    <p>
    Provides interfaces for Python file objects which allow structures of buffers to be created.  This is used to direct the output of components, subcomponents, filter sections, etc. to its final destination according to autoflush rules.
    </p>
    </&>
    <&|doclib.myt:item, name="HTTPHandler", description="HTTPHandler", &>
    <p>HTTPHandler is the base class for the the HTTP-oriented handlers, which includes
    ApacheHandler, CGIHandler, WSGIHandler, and HTTPServerHandler.</p>
    </&>
    <&|doclib.myt:item, name="util", description="util", &>
    <p>Util contains the data structure objects Value, ThreadLocal, OrderedDict as well as the cloning helper object ConstructorClone.</p>
    </&>
    <&|doclib.myt:item, name="synchronizer", description="synchronizer", &>
    <p>
    synchronizer contains code for synchronizing read and write operations on data structures against thread mutexes and file-based mutexes.  
    </p>
    </&>
    <&|doclib.myt:item, name="cache", description="cache", &>
    <p>
    The cache package provides the primary API for component output caching and data structure caching.
    </p>
    </&>
    <&|doclib.myt:item, name="container", description="container", &>
    <p>
    The container package provides a system of storing namespaces of key/value pairs in memory or filesystem based storage units, with additional support for DBM and memcached.  It is used as the common storage engine for the cache system as well as the session object.
    </p>
    </&>
    <&|doclib.myt:item, name="exception", description="exception", &>
    <p>
    The exception package defines a hierarchy of errors used across Myghty, as well as stack-trace formatting code used for logging and printing exceptions.
    </p>
    </&>

</&>


<&|doclib.myt:item, name="differences", description="Differences from HTML::Mason", &>
<p>Myghty is not the same as Mason.   Mason, which has established itself as a fast and efficient methodology for producing high capacity websites, has provided the initial starting point, but should the direction of Myghty go in a divergent direction, that is entirely OK.  When porting Mason to Myghty, opportunities arose to rework a lot of sections in new ways, and also to take advantage of the unique features of Python.  Browsing the source code of both applications can reveal a lot about this process.  </p>

<p>As far as the user experience as well as the internal architecture, beyond the obvious "its python, not perl" as well as the python indentation scheme, the differences between Myghty and Mason continue to mount, with some significant syntactical differences as well as executional differences:

<ul>
<li>%python tag contains the "scope" attribute, which effectively replaces %shared, %once, %init, %cleanup.  

<li>%args tag contains optional "scope" attribute, to specify component or request-scoped arguments

<li>%shared, %once, %init, %cleanup still exist, and %shared is also synonymous with %requestlocal and %requestonce, %once is synonymous with %global

<li>thread-scoped python was added, referenced by scope="thread" or alternatively %threadlocal, %threadonce

<li>the %flags section can also be specified inline inside the %method and %def tags as attributes

<li>filter sections and filter functions need to return a new instance of string with the filtered content since python strings are immutable.  Mason filters modify content in place.

<li>the %cleanup section is guaranteed to execute even in the case of components that raise an error, as the section is executed in a <&|formatting.myt:codeline&>finally</&> block.

<li>%cleanup is also available within methods and subcomponents

<li>additional component flags:  <&|formatting.myt:codeline&>autoflush</&> for fine-grained control of buffering,
<&|formatting.myt:codeline&>trim</&> for whitespace trimming of component output.  full cache functionality is available via the <&|formatting.myt:codeline&>use_cache</&> flag as well as all the options as <&|formatting.myt:codeline&>cache_XXXX</&>.

<li>the request object and component object interfaces were changed to be more pythonic, using properties as much as possible, as well as having different method names in some cases.  the execution model is a little different as well.

<li>module components architecture added, provides servlet-like objects to applications

<li>The m and r objects are available in request-scoped (%shared) and thread-scoped blocks

<li>ApacheHandler and CGIHandler were rewritten entirely.  They give their behavior to the Request object via their own implementations of RequestImpl.

<li>Caching API was rewritten entirely, and utilizes a genericized "container" API.  It includes a mutex-based "busy lock" feature.  The file storage system is DBM based.  Component caching can also be configured via the %flags section of any component to avoid the more complicated programmatic interface.

<li>Building off of the container API, a Session object is included in the base distribution which can also be configured as a global variable.

<li>The Mason strategy of <&|formatting.myt:codeline&>Class::Container</&> has been removed, and some of its functionality replaced with a small helper object called <&|formatting.myt:codeline&>myghty.util.ConstructorClone</&> that is used to create clones of objects.

<li>The <&|formatting.myt:codeline&>buffer</&> object was entirely rewritten as a hierarchy of classes that resemble Python's built-in file objects, and the attachment of buffers to each other is acheived through a "decorator" pattern.

<li>Object generation was completely rewritten using a "visitor" paradigm and is more decoupled from the Compiler.

<li>The Request object's context-specific behavior is provided by an internally-referenced RequestImpl object, which can be replaced with different implementations without the class of Request having to change.
</ul>

</p>
</&>







</&>
