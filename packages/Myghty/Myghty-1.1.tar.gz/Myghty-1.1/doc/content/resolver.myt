<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="resolver", description="Advanced Resolver Configuration"&>

<&|doclib.myt:item, name="intro", description="Introduction" &>
<p>With version 0.97 comes a new and highly configurable URI resolution engine.  This engine is responsible for converting the URI address of a component into a ComponentSource object, from which an actual Component is created.   Originally, components were only retrieved from one or more file-based component roots, configured by <& formatting.myt:link, path="parameters", param="component_root" &>.  Special logic existed for locating <& formatting.myt:link, path="specialtempl_dhandler" &> and <& formatting.myt:link, path="specialtempl_autohandler" &> components as well, and the resolution of URIs could be cached (i.e. <& formatting.myt:link, path="parameters", param="use_static_source" &>).   Myghty added the ability to load module-based components based on regular expressions (<& formatting.myt:link, path="parameters", param="module_components" &>), and also to translate incoming URIs via <& formatting.myt:link, path="parameters", param="path_translate"&>. </p>

<p>With the new resolution engine, it is now possible to:</p>
<ul>
	<li>Change the order of all resolution steps, or remove unneeded resolution steps.  The steps that can be controlled are component root lookup, module component lookup, path translation, dhandler resolution, autohandler resolution (also called 'upwards resolution'), and URI caching (static source).
	<li>Create conditional resolution rules or rule chains.  Built-in conditional rules allow matching the URI with a regular expression, or matching the "resolution context" of the incoming request.   Built-in resolution contexts include request, subrequest, component, and inherit.  User-defined resolution contexts can be created as well and specified in component lookup calls and also as the default context to be used in a subrequest.
	<li>Control the point at which the caching of URIs occurs, by placing a special rule above only those rules whose results should be reused, or to enable caching of just a single rule.
	<li>Inspect the full series of steps involved in a URI resolution via logging, regardless of whether or not it succeeded.  This is crucial for developing custom rule-chains.
	<li>Add special behavior to file-based resolution, so that the conversion from a URI to a filesystem path can be more than just a straight path concatenation of the component root and URI.
	<li>Retrieve an re.Match object that is created when a URI matches the regular expression used by a module component.  Capturing parenthesis can also be added to the regular expressions, whose results will also be available in the resulting Match object.
	<li>Create custom resolution rules using small and simple classes that can easily coexist with the built-in rules.
</ul>

</&>

<&|doclib.myt:item, name="step1", description="Basic Example"&>
Lets start with some component code that wants to locate another component:

<&|formatting.myt:code, syntaxtype="python"&>
	comp = m.fetch_component("/training/index.myt")
</&>
<p>
In the above line, the code is using the request to fetch the component referenced by the <b>uri</b> "/training/index.myt".  The process of looking up a component corresponding to a uri is called <b>resolution.</b> 
</p>


<p>When the resolver attempts to locate the uri, it executes a series of <b>resolver rules</b> specified within the configuration option <b>resolver_strategy</b>, which is represented as a list.  This list contains instances of one or more <span class="codeline">myghty.resolver.ResolverRule</span> subclasses, each of which represents a single rule along with configurational arguments for that rule.  A list of ResolverRule objects to be executed in order is also referred to as a <b>chain</b>.  A resolver strategy for the above search might look like:
</p>
<&|formatting.myt:code, syntaxtype="python"&>
	from myghty.resolver import *
	
	resolver_strategy = [
		ResolveFile(
			{'htdocs' : '/web/htdocs'}
		)
	]
</&> 

<p>Above, the resolver strategy has only one rule, an instance of <span class="codeline">ResolveFile</span>.  This rule searches through one or more component roots given as constructor arguments and concatenates the incoming URI to each root, until one of them matches an actual file located on the filesystem.  When a match is found, the rule cancels any further rule processing, and returns a result object from which the component can be loaded.  If no match is found, the rule passes control onto the next rule, or if no further rules exist, the resolver determines that the component cannot be located.  Since in the above example we have only one rule, if the file <span class="codeline">/web/htdocs/training/index.myt</span> doesn't exist, the fetch_component call will raise a <span class="codeline">ComponentNotFound</span> exception.</p>

<p>If no arguments are given to the constructor, ResolveFile instead uses the value of <&formatting.myt:link, path="parameters", param="component_root"&> as its list of roots.  From this one can see that when a Myghty installation specifies the component_root configuration parameter, this rule is implicitly activated behind the scenes. 
</p>

<p>The rule classes themselves require the symbols from the resolver package to be imported, as in <span class="codeline">from myghty.resolver import *</span>.  These symbols are also available in mod_python configuration within PythonOption directives, as of version 0.97a or the current CVS version.
</p>

<p>A few more rules can be added above, which allow more options for how this uri can be resolved:</p>


<&|formatting.myt:code, syntaxtype="python"&>
	from myghty.resolver import *

	resolver_strategy = [
		ResolveModule(
			{r'/user/.*' : 'myapp.UserManager'},
			{r'/admin/.*' : 'myapp.Administration'},
		),
		
		PathTranslate(
			(r'/training/' , r'/newmembers/'),
			(r'/$', '/index.myt'),
		),
		
		
		ResolveFile(
			{'htdocs' : '/web/htdocs'}
		)
	]
</&> 

<p>Two more rules have been added.  <span class="codeline">ResolveModule</span> will be the first to attempt resolving the uri, and it will attempt to match the uri against a series of regular expressions that each refer to a module component.  Module components are described in the section <&formatting.myt:link, path="modulecomponents"&>.  As our uri does not match either regular expression, the ResolveModule rule will give up, and pass control onto the next rule in the chain.  The ResolveModule rule, if instantiated with no arguments, will instead use the value of <&formatting.myt:link, path="parameters", param="module_components"&> as its list.  As with ResolveFile, when a Myghty installation specifies the module_components configuration parameter, this rule is also implicitly activated.
</p>

<p>Next is the <span class="codeline">PathTranslate</span> rule.  This rule is a <b>uri processing</b> rule which itself will never return a result, but rather changes the incoming uri and then passes the modified uri onto the remaining rules in the chain.  PathTranslate executes a series of regular expression search-and-replace operations on the uri before passing it on, which are specified as a list of two-element tuples.  PathTranslate, when given no arguments, will use the value of <&formatting.myt:link, path="parameters", param="path_translate"&> as its list.</p>

<p>We have specified a path translation rule that all uris starting with "/training/" should be changed to reference the same file within "/newmembers/" instead. Secondly, we specify that any uri which is a directory request, i.e. uris that end with a slash, should have the default file "index.myt" appended to it.  Our uri does match the first regular expression, so upon matching it will be converted into <span class="codeline">/newmembers/index.myt</span>.  We then arrive back at our ResolveFile rule, where either the existing file <span class="codeline">/web/htdocs/newmembers/index.myt</span> will be used as the source of the resolved component, or if no such file exists a <span class="codeline">ComponentNotFound</span> exception will be raised.</p>

<p class="tipbox">Behind the scenes, the <span class="codeline">myghty.resolver.Resolver</span> object is invoked to resolve the incoming uri, and when located it returns an instance of <span class="codeline">myghty.resolver.Resolution</span>, which in turn contains an instance of <span class="codeline">myghty.csource.ComponentSource</span>.  Whereas the Resolution instance describes just one of potentially many resolution paths the same component, the ComponentSource instance is the only object that describes location information for the component exactly.</p>   

</&>

<&|doclib.myt:item, name="realthing", description="The Real Set of Rules"&>
<p>The previous section illustrated the three basic ResolverRules that are behind the configuration parameters component_root, module_components, and path_translate.   In fact, these three rules also have an ordering that is used by default, and there are also several more rules installed by default which accomplish some other important tasks.   The default strategy is:</p>
<&|formatting.myt:code, syntaxtype="python"&>
	from myghty.resolver import *

	resolver_strategy = [
		PathTranslate(),
		ResolveDhandler(),
		URICache(),
		ResolveUpwards(),
		ResolveModule(),
		ResolvePathModule(),
		ResolveFile()
	]
</&>
<p>Our familiar rules PathTranslate, ResolveModule and ResolveFile are all present, and as they are specified with no constructor arguments they will use the values of their correspoinding configuration parameters.  Also one can see that path translation happens at the very front of everything before other resolution starts.  ResolvePathModule is also a new rule which corresponds to the configuration parameter <& formatting.myt:link, path="modulecomponents_resolution_module_root" &>.</p>

<p>Three new rules are introduced in this chain, <span class="codeline">ResolveDhandler</span>, <span class="codeline">URICache</span>, and <span class="codeline">ResolveUpwards</span>.  All have two things in common which are different from the first three rules:  they all are <b>conditional rules</b> that do not necessarily get activated, and also they are <b>rollup rules</b> which cannot resolve a component on their own, but rather rely upon the full list of rules that occur directly <b>below</b> them in order to retrieve results. </p>

<p>The <b>ResolveDhandler</b> rule is activated when the request looks for a top level component, with the option to serve a not-found component or directory request as a dhandler.  After not matching any resolution rules or file lookups for the given URI, it looks instead for /path/dhandler, and searches "upwards" through successive parent paths to resolve a dhandler.  The rules below are executed repeatedly with each new URI until a match is made, or no more path tokens exist.  Additionally, any resolved dhandlers that have been declined by the current request are also bypassed.  
</p>

<p>The <b>ResolveUpwards</b> rule is similar to the dhandler rule, except it is activated when a component searches for its inherited autohandler.  This rule also searches upwards through successive parent paths to locate the module or file.  In fact this rule can be used for any kind of upwards search but normally is used for autohandler only.
</p>


<p>The <b>URICache</b> rule caches the results of all rules below it, keyed against the incoming URI.  If the component is located, the resulting ComponentSource object is cached.  If it is not located,  the resulting ComponentNotFound condition is cached.  Whether or not this rule is enabled is based on the value of <&formatting.myt:link, path="parameters", param="use_static_source" &>.  URI caching has the effect of disabling repeated resolution/filesystem lookups for components that have already been located, as well as components that were not found when searched.   URICache also takes an optional constructor parameter source_cache_size, which indicates that this URICache should use its own cache of the given size, separately from the per-interpreter source cache.   Through custom configuration of URICache rules, parts of a site can be configured as static source and other parts can be configured as being more dynamically alterable.
</p>
<p>Since URICache caches data based only on the URI, it will complain if you try to put a dhandler rule below it.  This is because the dhandler rule does not necessarily return the same result for the same URI each time, as its upwards logic is conditionally enabled.  In theory, ResolveUpwards should have this effect as well, but since normal usage will use ResolveUpwards for all autohandlers and nothing else, it by default will not complain about a ResolveUpwards rule.  If you construct ResolveUpwards using <span class="codeline">ResolveUpwards(enable_caching = False)</span>, then the URICache rule will complain about it.
</p>
<p>
URICache also has an additional parameter which allows it to cache the results of just a single rule, instead of all rules below it:
</p>
<&|formatting.myt:code, syntaxtype="python"&>
	from myghty.resolver import *

	resolver_strategy = [
		URICache(rule = ResolveModule()),
		ResolveFile()
	]
</&>
<p>Above, only the results of ResolveModule will be cached.  ResolveFile will be executed every time it is called.</p>

</&>

<&|doclib.myt:item, name="conditionals", description="Conditionals, Groups and ConditionalGroups"&>
<p>Here is an example of conditional and group-based rules:
</p>
<&|formatting.myt:code, syntaxtype="python"&>
	from myghty.resolver import *

	resolver_strategy = [
		ConditionalGroup(context = 'subrequest', rules = [
			ResolveDhandler(),
			ResolveUpwards(),
			ResolveFile(),	
			NotFound()
		]),
		
		Conditional(regexp = '/login/.*', rule = ResolveModule({'.*' : 'myapp:LoginHandler'})),
		
		AdjustedResolveFile(
				adjust = [('/docs/', '/')], 
				('main' : '/web/htdocs'), 
				('comp' : '/web/comp') 
		)
	]
</&>

<p>
The above example routes all subrequests into a <b>rule subchain</b>, which resolves files only, including optional dhandler and autohandler resolution.    The subchain is <b>terminated</b> by the rule NotFound, which always results in a ComponentNotFound error.  If NotFound is not included, the resolution would fall through back into the main rule chain.  Continuing on, all non-subrequest component requests will first check for the URI '/login/' which matches to a specific module component, and then onto the bottom where it does a special file resolution rule.</p>

<p>That last rule above is AdjustedResolveFile(), which is a subclass of ResolveFile() that performs path translation on the incoming URI before concatenating it to each of its file paths.  In contrast to using PathTranslate(), the result of this translation is not propigated forward onto new requests nor is it used in the resulting component source; it is only used in the actual path concatenation.
</p>

</&>

<&|doclib.myt:item, name="context", description="Resolver Contexts"&>
<p>The Resolver is used for all resolution of URIs into components, which is not just the URI used by a client browser, but also URIs used for all components called by a template, the inheriting component of a template, and subrequests.  Custom resolver strategies allow different rules to execute based on this context, using the Conditional and ConditionalGroup rules.
</p>
<p>A common use for a conditional rule based on resolver context is to have module components be invoked only for request-based URIs, and all internal subreqests, component calls, and templates use file-based components:
</p>
<&|formatting.myt:code, syntaxtype="python"&>
	from myghty.resolver import *

	resolver_strategy = [
		ConditionalGroup(context = 'request', rules = [
			ResolveModule(),
			
			# optional - dont allow requests to "fall through"
			# into file-based resolution
			NotFound()
		]),
		
		ResolveDhandler(),
		URICache(),
		ResolveUpwards(),
		ResolveFile()
		
	]
</&>

<p>Above, all requests from the outside world must be resolved by module components, as the conditional is terminated by a NotFound() rule.  If the NotFound() rule is omitted, incoming uris that do not match a module component path will "fall through" into the file-based rules.</p>

<p>The resolver context is also customizable programmatically.  The request methods <&formatting.myt:link, path="request_methods", method="create_subrequest" &> and <&formatting.myt:link, path="request_methods", method="fetch_component" &> take the optional parameter <span class="codeline">resolver_context</span> which can be any user-defined string, or one of the standard names <span class="codeline">request, subrequest, component</span> or <span class="codeline">inherit</span>.   Any Conditional or ConditionalGroup rule which specifies the name as the value of <span class="codeline">context</span> will be activated by this name.
</p>
</&>

<&|doclib.myt:item, name="logging", description="Resolution Logging"&>
Details about a component resolution are attached to ComponentNotFound exceptions, when a page or component is not found.  Additionally, if you add the configuration parameter <span class="codeline">debug_elements = ['resolution']</span> to your Interpreter config, the resolution of all components will be logged.  This log details each step within a resolution with an identifying keyword, such as "resolvemodule:", "resolvefile:", or "dhandler".   See <&formatting.myt:link, path="parameters", param="debug_elements"&> for information on debug_elements.
</&>

<&|doclib.myt:item, name="custom", description="Custom Rules"&>
<p>The basic idea of a custom rule is to subclass the <span class="codeline">ResolverRule</span> class, overriding at least the <span class="codeline">do</span> method, which is tasked with returning a <span class="codeline">Resolution</span> object, which in turn contains a <span class="codeline">ComponentSource</span> object.
</p>
<p><b>Example 1 - File-based Custom Rule</b></p>
<&|formatting.myt:code, syntaxtype="python"&>
    from myghty.resolver import *
    from myghty.csource import *
    import os

    class MyFileResolver(ResolverRule):
        """a user-defined resolver rule that looks up file-based components"""
        def __init__(self, file_root):
            """builds a new MyFileResolver."""
            self.file_root = file_root
        
        def do_init_resolver(self, resolver, remaining_rules, **kwargs):
            """called when the MyFileResolver is established in the rule chain.
            'resolver' is the instance of Resolver being used to run the rules.
            'remaining_rules' is a list of all ResolverRules that occur below this rule.
            **kwargs receives the full dictionary of Myghty configuration parameters."""
            pass
        
        def do(self, uri, remaining, resolution_detail, **kwargs):
            """attempts to resolve the given uri into a Resolution object.
            'resolution_detail' is a list of log messages that will be appended to the debug log when 
            resolution is being logged, or to ComponentNotFound exceptions.
            **kwargs contains extra resolution arguments, such as "resolver_context" and "enable_dhandler". """
        
            if resolution_detail is not None: 
                resolution_detail.append("MyFileResolver:" + uri)

            # a simple resolution.
            file = self.file_root + uri
            if os.access(file, os.F_OK):
                # file exists, so return a Resolution/FileComponentSource
                return Resolution(
                        FileComponentSource(
                            file_path = file,
                            # file modification time - this is not required as of 0.99b
                            last_modified = os.stat(srcfile)[stat.ST_MTIME],
                            path = uri,
                            # key to identify the 'compilation root' for the component
                            path_id = 'myfileresolve',
                            # unique key to identify the component
                            id = "%s|%s" % (key, path), 
                        ), 
                        resolution_detail
                    )
            else:
                # file doesnt exist, so call the next resolver in the chain
                return remaining.next().do(uri, remaining, resolution_detail, **params)
</&>
<p><b>Example 2 - Module Component Custom Rule</b></p>
<&|formatting.myt:code, syntaxtype="python"&>
    from myghty.resolver import *
    from myghty.csource import *
    import sys, re
    
    class MyModuleResolver(ResolverRule):
        """a user-defined resolver rule that looks up module-based components"""
        def __init__(self, path):
            """constructs a new MyModuleResover with the given module path."""
            self.path = path

        def do_init_resolver(self, resolver, remaining_rules, **kwargs):
            """initializes the MyModuleResolver."""
            pass
            
        def do(self, uri, remaining, resolution_detail, context = None, **params):
            """resolves the given URI to a specific callable."""
            
            if resolution_detail is not None: 
                resolution_detail.append("MyModuleResolver: " + uri)

            # here we illustrate a variety of constructor arguments
            # for Resolution and ModuleComponentSource.
            if uri eq '/shopping/':
                # return a ModuleComponentSource with a callable inside of it
                # the "cache_arg" flag, new in version 0.99b, indicates that the 
                # given argument is not changing its type (i.e. function, object, class) and can be 
                # cached with regards to inspecting its type, parent module, etc.
                return Resolution(
                    ModuleComponentSource(shopping, cache_arg=True),
                    resolution_detail
                    )
            elif uri eq '/checkout/':
                # or with the standard "package.module:callable" string
                return Resolution(
                    ModuleComponentSource("mypackage.mymodule:checkout", cache_arg=True),
                    resolution_detail
                    )
            elif uri eq '/inspector/':
                # the Resolution object will also attach any additional **kwargs as attributes
                # which other components can then retreive via m.resolution
                return Resolution(
                    ModuleComponentSource(inspector, cache_arg=True),
                    resolution_detail
                    param1 = 'inspect',
                    param2 = 3
                    )
            else:
                # no component matches, return next resolver in the chain
                return remaining.next().do(uri, remaining, resolution_detail, **params)

</&>

<&|doclib.myt:item, name="installing", description="Installing the Rule"&>
<p>The new rule is then installed by specifying it within resolver_strategy, as in this example which first resolves via MyModuleResolver, and then resolves file components via MyFileResolver, plugged into the standard URICache/dhandler/autohandler chain:</p>
    
<&|formatting.myt:code, syntaxtype="python"&>
	from myghty.resolver import *

	resolver_strategy = [
	    MyModuleResolver('/usr/local/mymodules'),
	    ResolveDHandler(),
	    URICache(),
	    ResolveUpwards(),
	    MyFileResolver('/web/htdocs')
	]
</&>
</&>
</&>

</&>
