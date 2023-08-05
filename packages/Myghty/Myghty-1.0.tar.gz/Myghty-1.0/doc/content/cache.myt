<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="caching", description="Data Caching"&>
<p>Myghty provides the ability to cache any kind of data, including component output, component return values, and user-defined data structures, for fast re-retrieval.  All components, whether file-based or subcomponent, are provided with their own cache namespace, which in turn stores any number of key/value pairs.  Included with Myghty are implementations using files, dbm files, direct in-memory dictionaries, and <a href="http://www.danga.com/memcached/">memcached</a>.  User-defined implementations are also supported and can be specified at runtime.  The particular implementation used can optionally be specified on a per-key basis, so that any single namespace can store individual values across any number of implementations at the same time.</p>

<p>
Caching is generally used when there are process-intensive and/or slow operations that must be performed to produce output, and those operations also have little or no dependencies on external arguments, i.e. their value is not likely to change in response to request variables.   Examples of things that are good for caching include weather information, stock data, sports scores, news headlines, or anything other kind of data that can be expensive to retrieve and does not need to be updated with real-time frequency. 
</p>

<p>The front-end to the mechanism is provided by the <&|formatting.myt:codeline&>myghty.cache</&> package, and can be configured and used through global configuration parameters, per-component flags, and a programmatic interface.</p>


	<&|doclib.myt:item, name="component", description="Caching a Component's Output"&>
	<p>The simplest form of caching is the caching of a component's return value and output content via flags.  An example using a subcomponent (subcomponents are explained in <& formatting.myt:link, path="components_subcomponent"&>):</p>
	
	<&|formatting.myt:code&><%text>
		<%def heavytext>
			<%flags>
				use_cache = True
				cache_type = 'dbm'
				cache_expiretime = 30
			</%flags>
			<%init>
				data = big_long_query()
			</%init>
			Your big query returned: <% data.get_info() %>
		</%def>
	</%text></&>
	
	<p>In this example, the component's output text and its return value (if any) will be stored the first time it is called.  Any calls to this component within the next 30 seconds will automatically return the cached value, and the %init section and body will not be executed.  At the moment 30 seconds have elapsed, the first call to occur within this new period will result in the component executing in full again and recreating its output text and return value.  Subsequent calls that occur during this second execution will continue to return the prior value until the new value is complete.  Once the new value is complete, it is stored in the cache and the expiration counter begins again, for the next 30 seconds.</p>
	<p>Note that the parameter <&|formatting.myt:codeline&>cache_type</&> is set to <&|formatting.myt:codeline&>'dbm'</&>, which indicates that dbm-based caching is used.  This is the default setting when a data_dir parameter is configured with the Myghty application.   </p>

	<p>For components that contain a %filter section, the result of filtering is stored in the cache as well.  This allows the cache to be useful in limiting the execution of a process-intensive or time-consuming filtering function.
	</p>
	<p>
	When a component is recompiled, its cache contents are automatically expired, so that the cache can be refreshed with the value returned by the newly modified component.  This means it is safe to set a cache setting with no expire time at all for a component whose output never changes, and in fact such a component only executes once per compilation and never at all again, for the life of the cache.
	</p>
	</&>

	<&|doclib.myt:item, name="interface", description="Programmatic Interface"&>
	<p>The traditional caching interface looks like this:
	<&|formatting.myt:code&><%text>
	<%init>
		def create_data():
			return get_some_data()

		cache = m.get_cache()
		data = cache.get_value('mydata', type='memory', 
			createfunc=create_data, expiretime=60)
	</%init>
	</%text></&>
	Where "mydata" is a key that the data will be keyed upon, the type of cache is in memory only, the create_data() function is used to create the initial value of 'mydata' as well as regenerating it when it is expired, and the expire time is 60 seconds. </p>

	<p>The creation function argument is optional, and the cache can be populated externally as well:
	<&|formatting.myt:code&><%text>
	<%init>

		cache = m.get_cache()
		if not cache.has_key('mydata'):
			cache.set_value('mydata', get_some_data(), expiretime=60)

		data = cache.get_value('mydata')

	</%init>
	</%text></&>
	This is a more familiar way to check a dictionary for a value and set it.  However, the previous "creation function" methodology has a significant advantage, in that it allows the cache mechanism to execute the function in the context of a global "busy" lock, which prevents other processes and threads from executing the same function at the same time, and instead forces them to retrieve the previous expired value until the new value is completed.  If no previous value exists, they all wait for the single process/thread to create the new value.  For a creation function that is slow or uses a lot of resources, this limits those resources to only one concurrent usage at a time, and once a cache value exists, only one request will experience any slowness upon recreation.   
	</p>

	<p>To programmatically cache the output text of a component, use the <&|formatting.myt:codeline&>m.cache_self()</&> method on request, which is a <b>reentrant</b> component-calling method:
	<&|formatting.myt:code&><%text>
	<%init>
		if m.cache_self(key="mykey"):
			return
	</%init>

	# rest of component
	</%text></&>
	For an uncached component, the cache_self method will execute the current component a second time.  Upon the second execution, when the cache_self line is encountered the second time, it returns false and allows the component to complete its execution.   The return value and output is cached, after being sent through any output filters present.  Then returning up to the initial cache_self call, it returns true and delivers the components output and optionally its return value.  Filtering is also disabled in the component as it should have already occurred within the original caching step.  The process for an already cached component is that it simply returns true and delivers the component output.
	</p>
	<p>To get the component's return value via this method:
	<&|formatting.myt:code&><%text>
	<%init>
		ret = Value()
		if m.cache_self(key="mykey", retval = ret):
			return ret()

		# rest of component
		return 3 + 5
	</%init>
	</%text></&>
	A <b>value</b> object is used here to pass a return value via a method parameter.  The return value is simply the cached return value of the component.
	</p>

	<p>
	Generally, the %flags method of caching a component's output and return value is a lot easier than the programmatic interface.  The main advantage of the programmatic interface is if the actual key is to be programmatically decided based on component arguments it can be figured out at runtime and sent as the "key" argument.  This also applies if any of the other properties of the cache are to be determined at run-time rather than compile time.
	</p>
	</&>

	<&|doclib.myt:item, name="details", description="More on Caching"&>
	<p>The cached information may be shared within the scope of one process or across multiple processes. Synchronization mechanisms are used to insure that the regeneration is only called by one thread of one process at a time, returning the expired value to other processes and threads while the regeneration is occuring.  This maximizes performance even for a very slow data-regeneration mechanism.  In the case of a non-memory-based cache, an external process can also access the same cache. </p>

	<p>Note that Myghty only includes thread-scoped synchronization for the Windows platform (contributors feel free to contribute a Win32 file locking scheme).  The "file" and "dbm" cache methodologies therefore may not be entirely synchronized across multiple processes on Windows.  This only occurs if multiple servers are running against the same cache since Windows doesnt have any forking capability and therefore an Apache server or similar is only using threads.
</p>

	<p>Caching has an assortment of container methodolgies, such as <&|formatting.myt:codeline&>MemoryContainer</&> and <&|formatting.myt:codeline&>DBMContainer</&>, and provides a base Container class that can be subclassed to add new methodologies.  A single component's cache can have containers of any number of different types and configurations.</p>
	<p>
     	Caching of the URI resolution step can also be done to improve performance.  See <&formatting.myt:link, path="parameters", param="use_static_source"&> for more information on using the URICache.
    </p>

	</&>

	<&|doclib.myt:item, name="options", description="Cache Options"&>
	<p>Caching options are all specified as Myghty configuration parameters in the form <&|formatting.myt:codeline&>cache_XXXX</&>, to identify them as options being sent to the Cache object.  When calling the m.get_cache() method, parameters may be specified with or without the <span class="codeline">cache_</span> prefix; they are stripped off.   While some cache options apply to the Cache object itself, others apply to specific forms of the Container class, the two current classes being <&|formatting.myt:codeline&>MemoryContainer</&> and <&|formatting.myt:codeline&>DBMContainer</&>.</p>
	<p>The full list of current options is as follows:</p>

	<&|formatting.myt:paramtable&>

	<&|formatting.myt:param, name="cache_container_class", classname="Cache", type="class object" , users =None&>
	This is a class object which is expected to be a subclass of <&|formatting.myt:codeline&>myghty.container.Container</&>, which will be used to provide containment services.  This option need only be used in the case of a user-defined container class that is not built into the static list of options in the Cache class.  To use one of the built in container classes, use <&|formatting.myt:codeline&>cache_type</&> instead.
	</&>
	<&|formatting.myt:param, name="cache_data_dir", classname="DBMContainer", type="string", default="same as Interpreter data_dir", users=None &>
	This is the data directory to be used by the DBMContainer (file-based cache) to store its DBM files as well as its lockfiles.  It is set by default to be the same as the data_dir parameter for the Myghty application.  As it creates its own subdirectories for its files (as does Interpreter), the files are kept separate from Myghty compiled pages.
	</&>
	<&|formatting.myt:param, name="cache_dbm_dir", classname="DBMContainer", type="string", default="cache_data_dir + '/container_dbm'", users=None &>
	This value indicates the directory in which to create the dbm files used by DBMContainer; if not present, defaults to a subdirectory beneath <&|formatting.myt:codeline&>cache_data_dir</&>.
	</&>
	<&|formatting.myt:param, name="cache_dbmmodule", classname="DBMContainer", type="module", default="anydbm", users=None &>
	<p>DBMContainer uses dbm files via the Python built-in <&|formatting.myt:codeline&>anydbm</&> module, which searches for a platform specific dbm module to use.  Any Python dbm module can be specified here in place of it.  To specify this option under mod_python as an Apache configuration directive, use this format:</p>
	<&|formatting.myt:code&><%text>
		PythonOption MyghtyCacheDbmmodule "__import__('gdbm')"
	</%text></&>
	</&>

	<&|formatting.myt:param, name="cache_debug_file", classname="Cache", type="file object", users=None &>
		If pointing to a Python file object, container operations performed by the caching system will be logged, allowing the viewing of how often data is being refreshed as well as how many concurrent threads and processes are hitting various containers.
	When running with ApacheHandler or CGIHandler, this parameter can be set to the standard Apache log via the 
	parameter <&|formatting.myt:codeline&>log_cache_operations</&>.
	</&>

	<&|formatting.myt:param, name="cache_lock_dir", classname="DBMContainer", type="string", default="cache_data_dir + '/container_dbm_lock'", users=None &>
	This value indicates the directory in which to create the lock files used by DBMContainer; if not present, defaults to a subdirectory beneath <&|formatting.myt:codeline&>cache_data_dir</&>.
	</&>
	<&|formatting.myt:param, name="cache_url", classname="MemcachedNamespaceManager", type="string", default="None", users=None &>
	The memcached URL to connect to for memcached usage, e.g. "localhost:11211".
	</&>

	<&|formatting.myt:param, name="cache_type", classname="Cache", type="module", users =None, default="file or memory" &>
	<p>This is the type of container being used.  Current options are <&|formatting.myt:codeline&>file</&>, <&|formatting.myt:codeline&>dbm</&>, <&|formatting.myt:codeline&>memory</&>, and <&|formatting.myt:codeline&>ext:memcached</&>.</p>

	<p>This option defaults to <&|formatting.myt:codeline&>dbm</&> if a <&|formatting.myt:codeline&>data_dir</&> option is present in the current application, else uses <&|formatting.myt:codeline&>memory</&>.</p>

	</&>

	<&|formatting.myt:param, name="log_cache_operations", classname="ApacheHandler or CGIHandler", type="boolean", default="False", users=None &>
	Sets the Cache <&|formatting.myt:codeline&>cache_debug_file</&> argument to point to the Apache error log or standard error output.  See <&|formatting.myt:codeline&>cache_debug_file</&>.
	</&>

	</&>
	</&>

	<&|doclib.myt:item, name="types", description="Cache Types"&>
	<ul>
		<li>'dbm' - uses the <span class="codeline">anydbm</span> module combined with <span class="codeline">cPickle</span> to store data.</li>
		<li>'file' - uses the <span class="codeline">cPickle</span> module combined with regular file access to store data.  This method may be faster than 'dbm' if the entire contents of the file are retrieved often, whereas dbm is faster for pulling a single key out of a larger set of data.</li>
		<li>'memory' - uses a regular Python dictionary.  Speed is the fastest, but the cache is not useable across processes nor is it persistent across server restarts.  It also has the highest utilization of RAM.</li>
		<li>'ext:memcached' - uses <a href="http://www.danga.com/memcached/">memcached</a> for caching and requires the Python memcached module to be installed.</li>
	</ul>
 	
	</&>
</&>
