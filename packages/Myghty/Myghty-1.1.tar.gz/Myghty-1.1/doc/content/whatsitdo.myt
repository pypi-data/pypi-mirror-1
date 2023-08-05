<%flags>inherit='document_base.myt'</%flags>



<&|doclib.myt:item, name="whatdoesitdo", description="What does Myghty Do?", header="Introduction" &>
<p>Heres a rundown of what Myghty is about, touching upon the basic features one would expect in a template system, as well as the unique features Myghty provides.
</p>

<&|doclib.myt:item, name="psp", description="High Performance Python Server Pages (PSP)"&>
<p>Myghty's primary feature is it's <b>Python Server Page (PSP)</b> system.  Individual templates are generated into pure Python modules which become the method of serving the content.   Myghty creates real Python modules from templates, which are regular .py files with corresponding .pyc bytecode files.  These modules can also be generated in memory only, if desired.</p>

<p>Myghty templates allow full Python syntax to be embedded amongst HTML or other markup, and keeps intact the <b>full syntax and indentation scheme</b> of Python, even within very markup-interactive sections of code.  Myghty also lets you organize embedded Python code in ways that minimize its intrusion upon markup.  Python embedded within markup is clearly denoted via <% "<%python>" %> tags or the more interactive "%" syntax:</p>

	<&|formatting.myt:code &>
	<%text>
	<%python>
		def somefunc():
			return True
	</%python>
	
	% if somefunc():
	<p>
		hello!
	</p>
	% # end for
	</%text>
	</&>
<p>Read more about Myghty syntax in <& formatting.myt:link, path="embedding" &>.</p>
<p>
Python sections can optionally have scope attributes specified, with values such as "global", "request", "init" and "cleanup", which cause the contained python code to execute at specific points in the template's execution, regardless of where they are placed in the template.  This allows flexible organization of template code and a very distinct separation of Python and markup.   Read more about Myghty code scope in <& formatting.myt:link, path="scopedpython" &>.</p>
</&>

<&|doclib.myt:item, name="components", description="Componentized Development"&>
<p>Myghty allows you to organize Python code and markup into smaller sub-units of a page called <b>Components</b>.  Consider a page like this:</p>

<pre>
                        +--------------------+
                        |    |    toolbar    |
                        |    +---------------|
                        |  header            |
                        |--------------------|
                        |        |           |
                        | left   |           |
                        | nav    | content   |
                        |        |           |
                        |        |           |
                        |--------------------|
                        |        footer      |
                        +--------------------+
</pre>

<p>Each subsection of this page is a likely candidate to be its own <b>component</b>.  The overall template is referred to as the <b>top-level component</b>, and contains any number of <b>subcomponents</b>, which are effectively semi-autonomous units of code within a larger template file.  They have their own namespaces, passed-in argument lists, buffering and caching attributes, etc.  Components normally send their output to the current output stream, but can also be called as Python functions with return values, or their output content can be grabbed into a string as the return value.</p>

<p>All components are capable of calling any other component within the same template, and also of calling another template to be executed inline, or even the subcomponents contained within other templates, which are known as <b>methods</b>.  With these functions, the page above can be organized into any variety of HTML/python code-snippets either within a single template file or across any combination of template and/or method library files:</p>


<pre>
           components.myt
        +-----------------+                                      
        |                 |                              page.myt
        |                 |       header.myt        +---------------+
        |  +-----------+  |    +---------------+    |   **********  |
        |  | toolbar   |--------------->*****  |------> **********  |
        |  +-----------+  |    |    header     |    |               |
        |                 |    +---------------+    | **            |
        |    +------+     |                         | **    page    |
        |    |      |     |                         | **   content  |
        |    | left | ------------------------------->**            |
        |    | nav  |     |                         | **            |
        |    |      |     |                         |               |
        |    +------+     |                         | +-----------+ |
        |                 |                         | |  footer   | |
        +-----------------+                         | +-----------+ |
                                                    +---------------+
                                       
                                    
</pre>




<p>Components are called via the <% "<& &>" | h%> tag construct, and also support "open-tag/close-tag" behavior via the <% "<&| &></&>" | h%> syntax, known as a <b>component call with content</b>.  The content within the tags is enclosed into its own Python function that is callable by the component code, allowing custom tags with full control of execution to be created.
</p>
<p>Read more about Myghty components in <& formatting.myt:link, path="components" &>.</p>
</&>

<&|doclib.myt:item, name="modulecomponents", description="Module Components"&>
<p>Myghty introduces a convenient environment-agnostic way to mix regular Python modules with template code known as Module Components.  The same component model that applies to templates can be applied to regular Python objects and functions, either by explicitly subclassing the ModuleComponent class in a manner similar to a Servlet, or by configuring Myghty to implicitly resolve any regular Python function, callable object, or plain object instance into a FunctionComponent (version 0.98).</p>

<p>Module Components serve primarily as the "controller" stage in a request, the initial entry point for a request that handles data loading and state changes, and then passes control onto a template for display.  As they are also fully capable component objects, they can also just as easily be embedded within templates, either by themselves or wrapped around further sub-content, to allow the creation of module-based tag libraries.</p>

<p>A big advantage to using Module Components for controller code is that the application remains completely portable to any environment, including mod_python, any WSGI environment, or non-web oriented environments.</p>

<p>Read more about Myghty Module Components in <& formatting.myt:link, path="modulecomponents" &>.</p>
</&>

<&|doclib.myt:item, name="inheritance", description="Page Inheritance"&>
<p>Any top level component can also be <b>inherited</b> by another top level component.  This means the execution of pages can be implicitly or explicitly "wrapped" by an enclosing template, which can control the execution and content embedding of its "subtemplate" at any point in its execution.  In the diagram below, a content-based HTML file is enclosed by a file providing a standardized layout, which is enclosed by another file that provides session authentication code and management:
</p>

<pre>
        /lib/authenticate.myt
        +------------------+
        |% authenticate()  |
        |-------------------             /autohandler
        |                  |         +-----------------+                
        |                            |      header     |    /foo/content.myt
        |                            |-----------------|      +--------+
        |    m.call_next() --->      |                        |        |
        |                            |   m.call_next() --->   |content |
        |                            |                        |        |
        |                  |         |-----------------|      +--------+
        |------------------|         |      footer     |                
        |% cleanup()       |         +-----------------+                
        +------------------+
</pre>

<p>The methods of a parent template are also inherited by the child and can also be overridden, allowing a sub-template to change the behavior of its parent.    Layout and behavior of individual groups of templates, directories, or entire sites can be managed through a concise and centralized group of inheritable templates.
</p>

<p>Read more about Inheritance in <& formatting.myt:link, path="inheritance" &>.</p>

</&>

<&|doclib.myt:item, name="performance", description="Performance"&>
<p>Myghty is written with fast performance and highly concurrent service in mind.  A flexible cache API, supporting in-memory, file, DBM and Memcached backends allows quick re-delivery of complicated pages.  Buffering can be completely disabled, for an entire site or just individual pages,  to send template output to directly to the client.  Expensive cache and compilation operations are process- and thread-synchronized to prevent data corruption and redundant computation.  A configurable least-recently-used cache holds only the most heavily used components in memory, deferring less used ones to be loaded again from .pyc files.  Filesystem checks can be disabled as well, allowing complete in-memory operation.  Large chunks of plain text are distilled into large, multi-line write() statements to minimize method call overhead for large and mostly static pages.</p>
</&>

<&|doclib.myt:item, name="other", description="Other Features"&>
<ul>
	<li> Session object support - can write session data into memory, plain or DBM files, or Memcached.
	<li> Direct connectors for mod_python, CGI, WSGI, Python Paste, SimpleHTTPServer.  As the Interpreter object is a lightweight object with no external dependencies whatsoever, any Python application or application server can invoke any series of Myghty components with just one line of code.
	<li> A super-configurable ruleset driven URI resolution architecture allowing many options for resolving URI's both externally and within templates.  Allows any combination of resolution directly to templates, Module Components, or any plain Python function or object instance.   Special rules exist to route non-existent URI's to specific components, to cache the results of URI resolution for higher performance, and to execute conditionally based on contextual information.
	<li>Cache API and implementation, can cache component output and any other data structure in memory, in plain files, DBM files, or Memcached.  Includes a "busy lock" feature that allows a slow re-generation method to execute while the old data continues to be returned to other threads and processes.  New cache implementations can be added fairly easily.
	<li> Flexible global namespaces allow components to have any number of custom "global" variables.
	<li> Special code blocks allow the construction of code that is local to the current request,  or local to the current thread.  A ThreadLocal object is supplied as well for safe management of thread-sensitive resources such as databases.
	<li> Fine grained control of buffering - the buffering of textual output as it is delivered to the client can controlled at the application, page, or component level.
	<li> Custom filtering functions can be defined for the output any component, within the source of the component via the <% "<%filter>" %> tag.  
	<li> Full featured error handling and reporting.  errors can be logged to the Apache logs or standard error, caught by application code, and/or reported to the browser screen.  stack traces are delivered showing original template line numbers.
</ul>
</&>

</&>
