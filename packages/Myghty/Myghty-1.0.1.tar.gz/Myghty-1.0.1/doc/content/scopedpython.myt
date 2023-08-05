<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="scopedpython", description="Scoped <%python> Blocks", &>
	<p>The <% "<%python>" %> tag is also capable of specifying Python code that occurs within a specific scope of a template's execution, using the <&|formatting.myt:codeline&>scope</&> attribute.   Scopes are provided that specify Python code as always the first thing executed within a component, always the last thing executed, or executes once per request, once per application thread, or once per application process.</p>
	
	<p>Originally, these scopes had their own specific tag names, which are still available.  These names include all those that are familiar to HTML::Mason users, as well as some new names.  All synonyms are noted in each section.  </p>

	<&|doclib.myt:item, name="component", description="Component Scope", escapedesc=True &>
	<p><b>Usage:</b>  <% '<%python scope="component">' %></p>
	<p><b>Also called:</b>  <% "<%python>" %></p>
	<p>A component-scoped block is a regular block of Python that executes within the body of a template, as illustrated in the previous section <&formatting.myt:link, path="embedding_blocks"&> .  Many component-scoped blocks may exist in a template and they will all be executed in the place that they occur.  Component scope has two variants, init and cleanup scope, which while still being component scope, execute at specific times in a component's execution regardless of their position in a template.  They are described later in this section.</p>
	
	</&>
	
	<&|doclib.myt:item, name="global", description="Global Scope", escapedesc=True &>
	<p><b>Usage:</b>  <% '<%python scope="global">' %></p>
	<p><b>Also called:</b>  <% "<%global>" %>, <% "<%once>" %> </p>
	<p>A global-scoped block refers to a section of Python code that is executed exactly once for a component, within the scope of its process.  In reality, this usually means code that is executed each time the module is newly loaded or reloaded in the current Python process, as it is called as part of the module import process.  Variables that are declared in a global-scoped block are compiled as global variables at the top of the generated module, and thus can be seen from within the bodies of all components defined within the module.  Assignment to these variables follows the Python scoping rules, meaning that they will magically be copied into local variables once assigned to unless they are pre-declared in the local block with the Python keyword <&|formatting.myt:codeline&>global</&>.</p>
	
	<p>Global-scoped Python executes only once when a component module is first loaded, as part of its import.  As such, it is called slightly outside of the normal request call-chain and does not have the usual access to the the built-in request-scoped variables <i>m</i>, <i>r</i>, ARGS, etc.  However, you can access the Request that is corresponding to this very first execution via the static call <&|formatting.myt:codeline&>request.instance()</&>, which will give you the current request instance that is servicing the global-scoped block. </p>

	<&|formatting.myt:code&>
	<%text>
	<%python scope="global">
		# declare global variables, accessible
		# across this component's generated module
		
		message1 = "this is message one."
		message2 = "this is message two."
		message3 = "doh, im message three."
	</%python>
	
	<%python>
		# reference the global variables
		m.write("message one: " + message1)
		m.write("message two: " + message2)
		
		# we want to assign to message3,
		# so declare "global" first
		global message3
		
		message3 = "this is message three."
		
		m.write("message three: " + message3)
		
	</%python>
	</%text>
	</&>
	
	<p>Use a global-scoped Python block to declare constants and resources which are shareable amongst all components within a template file.  Note that for a threaded environment, global-scoped section applies to all threads within a process.  This may not be appropriate for certain kinds of non-threadsafe resources, such as database handles, certain dbm modules, etc.  For thread-local global variable declaration, see the section <&formatting.myt:link, path="scopedpython_thread"&>, or use the Myghty <&|formatting.myt:codeline&>ThreadLocal()</&> object described in <&formatting.myt:link, path="scopedpython_thread_threadlocal"&>.  Similarly, request-scoped operation is provided as well, described in the section <&formatting.myt:link, path="scopedpython_request"&>.</p>
	
	<p>A global-scoped block can only be placed in a top-level component, i.e. cannot be used within %def or %method.</p>
	</&>



	<&|doclib.myt:item, name="init", description="Init Scope", escapedesc=True &>

	<p><b>Usage:</b> <% '<%python scope="init">' %>
	<p><b>Also called:</b> <% "<%init>" %></p>

	<p>Init-scoped Python is python code that is executed once per component execution, before any other local python code or text is processed.  It really is just a variant of component scope, since it is still technically within component scope, just executed before any other component-scoped code executes.    One handy thing about init scope is that you can stick it at the <i>bottom</i> of a big HTML file, or in any other weird place, and it will still execute before all the other local code.  Its recommended as the place for setting up HTTP headers which can only be set before any content and/or whitespace is written (although if autoflush is disabled, this is less of an issue; see <&formatting.myt:link, path="filtering_autoflush"&> for more details).</p>
	
	<p>In this example, a login function is queried to detect if the current browser is a logged in user.  If not, the component wants to redirect to a login page.  Since a redirect should occur before any output is generated, the login function and redirect occurs within an init-scoped Python block:</p>
	
	<&|formatting.myt:code&><%text>
	<%python scope="init">
		# check that the user is logged in, else
		# redirect them to a login page
		if not user_logged_in():
			m.send_redirect("/login.myt", hard = True)
	</%python>	

	<%doc>rest of page follows....</%doc>	
	<html>
		<head>
		....
		
	
	</%text></&>
	
	</&>


	<&|doclib.myt:item, name="cleanup", description="Cleanup Scope", escapedesc=True &>
	<p><b>Usage:</b> <% '<%python scope="cleanup">' %>
	<p><b>Also called:</b> <% "<%cleanup>" %></p>

	<p>Cleanup-scoped Python is Python code executed at the end of everything else within a component's execution.  It is executed within the scope of a <&|formatting.myt:codeline&>try..finally</&> construct so its guaranteed to execute even in the case of an error condition.</p>
	
	<p>In this example, a hypothetical LDAP database is accessed to get user information.  Since the database connection is opened within the scope of the component inside its init-scoped block, it is closed within the cleanup-scoped block:</p>

	<&|formatting.myt:code&><%text>
	<%args>
		userid
	</%args>
	<%python scope="init">
		# open a connection to an expensive resource
		ldap = Ldap.connect()
		userrec = ldap.lookup(userid)
	</%python>
		
		name: <% userrec['name'] %><br/>
		address: <% userrec['address'] %><br/>
		email: <% userrec['email'] %><br/>
		
	<%python scope="cleanup">
		# insure the expensive resource is closed
		if ldap is not None:
			ldap.close()
	</%python>
	</%text></&>
	
	</&>


	<&|doclib.myt:item, name="request", description="Request Scope", escapedesc=True &>

	<p><b>Usage:</b> <% '<%python scope="request">' %>
	<p><b>Also called:</b> <% "<%requestlocal>, <%requestonce> or <%shared>" %></p>
	
	<p>A request-scoped Python block has similarities to a global-scoped block, except instead of executing at the top of the generated component's module, it is executed within the context of a function definition that is executed once per request.  Within this function definition, all the rest of the component's functions and variable namespaces are declared, so that when variables, functions and objects declared within this function are referenced, they are effectively unique to the individual request.</p>

	<&|formatting.myt:code&><%text>
	<%python scope="request">
		context = {}
	</%python>

	% context['start'] = True
	<& dosomething &>

	<%def dosomething>
	% if context.has_key('start'):
		hi
	% else:
		bye
	</%def>
	</%text></&>
	
	
	<p>The good news is, the regular Myghty variables <i>m</i>, <i>ARGS</i>, <i>r</i> etc. are all available within a request-scoped block.  Although since a request-scoped block executes within a unique place in the call-chain, the full functionality of <i>m</i>, such as component calling, is not currently supported within such a block.</p>

	<p>Request-scoped sections can only be used in top-level components, i.e. cannot be used within %def or %method.</p>	

	<&|doclib.myt:item, name="value", description="Using Pass-By-Value", escapedesc=True &>
	
	<p>While the net result of a request-scoped Python block looks similar to a global-scoped block, there are differences with how declared variables are referenced.  Since they are not module-level variables, they can't be used with the Python <&|formatting.myt:codeline&>global</&> keyword.  There actually is no way to directly change what a request-scoped variable points to; however this can be easily worked around through the use of pass-by-value variables.  A pass-by-value effect can be achieved with an array, a dictionary, a user-defined object whose value can change, or the automatically imported Myghty datatype <&|formatting.myt:codeline&>Value()</&>, which represents an object whose contents you can change:</p>
	
	<&|formatting.myt:code&><%text>
	<%python scope="request">
		status = Value("initial status")
	</%python>

	<%python>
		if some_status_changed():
			status.assign("new status")
	</%python>

	the status is <% status() %>
	</%text></&>
	</&>

	<&|doclib.myt:item, name="alternative", description="Alternative - Request Attributes", escapedesc=True &>
	
	<p>An alternative to using request-scoped blocks is to assign attributes to the request object, which can then be accessed by any other component within that request.  This is achieved via the member <&formatting.myt:link, path="request_members", member="attributes" &>:</p>
	<&|formatting.myt:code&><%text>
	<%python>
	m.attributes['whatmawsaw'] = 'i just saw a flyin turkey!'
	</%python>

	# .... somewhere in some other part of the template


	JIMMY: Hey maw, what'd ya see ?  
	MAW: <% m.attributes['whatmawsaw'] %>
	</%text></&>
	<p>Produces:</p>
	<&|formatting.myt:code&>
		JIMMY: Hey maw, what'd ya see ?
		MAW: i just saw a flyin turkey!
 	</&>
 	
 	<p>Also see <&formatting.myt:link, path="request" &> which lists all request methods, including those used for attributes.
 	</p>
 	</&>
 	
	</&>



	<&|doclib.myt:item, name="thread", description="Thread Scope", escapedesc=True &>
	
	<p><b>Usage:</b>  <% '<%python scope="thread">' %></p>
	<p><b>Also called:</b> <% "<%threadlocal>" %>, <% "<%threadonce>" %></p>
	
	<p>A thread-scoped Python block is nearly the same as a <&formatting.myt:link, path="scopedpython_request"&> block, except its defining function is executed once per thread of execution, rather than once per request.  In a non-threaded environment, this amounts to once per process.  The standard global variables <i>m</i>, <i>r</i> etc. are still available, but their usefulness is limited, as they only represent the one particular request that happens to be the first request to execute within the current thread.  Also, like request-scope, variables declared in a thread-scoped block cannot be changed except with pass-by-value techniques, described in <&formatting.myt:link, path="scopedpython_request_value"&></p>
	
	<p>In this example, a <&|formatting.myt:codeline&>gdbm</&> file-based database is accessed to retreive weather information keyed off of a zipcode.  Since gdbm uses the 
	<&|formatting.myt:codeline&>flock()</&> system call, it's a good idea to keep the reference to a gdbm handle local to a particular thread (at least, the thread that opens the database must be the one that closes it).  The reference to gdbm is created and initialized within a thread-scoped block to insure this behavior:</p>
	
	<&|formatting.myt:code&><%text>
	<%python scope="thread">
		# use GNU dbm, which definitely doesnt work in 
		# multiple threads (unless you specify 'u')
		import gdbm
		db = gdbm.open("weather.dbm", 'r')
	</%python>

	<%args>
		zipcode
	</%args>
	
	temperature in your zip for today is: <% db[zipcode] %>
	
	</%text></&>
	<p>Use a thread-scoped block to declare global resources which are not thread-safe.  A big candidate for this is a database connection, or an object that contains a database-connection reference, for applications that are not trying too hard to separate their presentation code from their business logic (which, of course, they should be).  </p>

	<p>Thread-scoped sections can only be used in top-level components, i.e. cannot be used within %def or %method.</p>	

	<&|doclib.myt:item, name="threadlocal", description="Alternative to Thread Scope: ThreadLocal()", escapedesc=True &>

	<p>A possibly higher-performing alternative to a thread-scoped section is to declare thread-local variables via the automatically imported class <&|formatting.myt:codeline&>ThreadLocal()</&>.  The <&|formatting.myt:codeline&>ThreadLocal()</&> class works similarly to a <&|formatting.myt:codeline&>Value()</&> object, except that assigning and retrieving its value attaches the data internally to a dictionary, keyed off of an identifier for the current thread.  In this way each value can only be accessed by the thread which assigned the value, and other threads are left to assign their own value:</p>

	<&|formatting.myt:code&><%text>
	<%python scope="global">
		x = ThreadLocal()
	</%python>

	<%python>
		import time
		x.assign("the current time is " + repr(time.time()))
	</%python>
	
	value of x: <% x() %>
	
	</%text></&>

	<p><&|formatting.myt:codeline&>ThreadLocal()</&> also supports automatic creation of its value per thread, by supplying a pointer to a function to the parameter <&|formatting.myt:codeline&>creator</&>.  Here is the above gdbm example with <&|formatting.myt:codeline&>ThreadLocal()</&>, using an anonymous (lambda) creation function to automatically allocate a new <&|formatting.myt:codeline&>gdbm</&> handle per thread:</p>
	<&|formatting.myt:code&><%text>
	<%python scope="global">
		import gdbm
		db = ThreadLocal(creator = lambda: gdbm.open("weather.dbm", 'r'))
	</%python>

	<%args>
		zipcode
	</%args>
	
	temperature in your zip for today is: <% db()[zipcode] %>

	</%text></&>
	
	</&>
	
	</&>


</&>


