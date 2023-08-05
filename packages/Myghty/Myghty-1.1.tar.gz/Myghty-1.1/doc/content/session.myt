<%flags>inherit='document_base.myt'</%flags>

<&|doclib.myt:item, name="session", description="Session", &>
<p>Myghty now has its own session storage class.  This class offers some advantages over the mod python session, including:</p>
<ul>
	<li>It is independent of mod_python, so it works with either version of Apache, other web connectors, and in CGI mode
	<li>The file-based version keeps each user's session in separate DBM files, so no synchronization issues are present
	between disparate sessions, session files are small, and old sessions can be cleaned up via an external file-deletion process.
	<li>The session object loads its data in immediately from the persistent store and unlocks, so that a page containing multiple session-enabled requests (i.e., such as a page with IFRAMEs or image delivery servlets) can allow access to all of its sub-elements with a minimum of waiting between the concurrent requests.
	<li>The package can also run directly with the mod_python request, independently of Myghty.
</ul>

<&|doclib.myt:item, name="usage", description="Basic Usage", &>
<p>The session is retrieved from the request object via the get_session() method, operated upon like a dictionary, and then can have its <span class="codeline">save()</span> method called to write its data to persistent storage:</p>


	<&|formatting.myt:code&><%text>
	<%python scope="init">
		# get the session
		session = m.get_session()
		
		# add data
		session['key1'] = 'foo'
		
		# get data
		if session.has_key('user'):
			user = session['user']
		else:
			user = User()
			session['user'] = user
			
		# save new information
		session.save()
	</%python>
	</%text></&>

<p>The session handles generation of session IDs automatically as well as storing and retrieving them from cookies.  Options exist to pass in custom session IDs, to not use cookies, to use "signed" session IDs, and to change the cookie-based session key (defaulting to <span class="codeline">myghty_session_id</span>).  It loads its data in fully when instantiated and then unlocks, so no programmatic locking or unlocking is necessary (but lock methods are available if you want the session to stay locked throughout a request).</p>

</&>

<&|doclib.myt:item, name="options", description="Session Options", &>

	
<p>Session options are specified as Myghty configuration parameters in the form <&|formatting.myt:codeline&>session_XXXX</&>, to identify them as options being sent to the Session object.   When calling the m.get_session() method, parameters may be specified with or without the "session_" prefix; they are stripped off. </p>

<p>The get_session method can take any of the configuration parameters that are identified below as used directly by the Session object or by the underlying Namespace objects.</p>


	<&|formatting.myt:paramtable&>

	<&|formatting.myt:param, name="session_cookie_expires", classname="Session", type="boolean, datetime, timedelta", users=None, default="True" &>
	The expiration time to use on the session cookie.  Defaults to "True" which means, dont specify any expiration time (the cookie will expire when the browser is closed).  A value of "False" means, never expire (specifies the maximum date that can be stored in a datetime object and uses that).  The value can also be a datetime.timedelta() object which will be added to the current date and time, or a datetime.datetime() object.
	</&>


	<&|formatting.myt:param, name="session_data_dir", classname="Session", type="string", users=None &>
	The data directory where sessions will be stored.  If this argument is not present, the regular
	<&formatting.myt:link, path="parameters", param="data_dir"&> parameter is used, with the path "./sessions" appended to it.
	</&>

	<&|formatting.myt:param, name="session_dbmmodule", classname="DBMNamespace", type="dbm module", users=None, default='anydbm' &>
	When dbm is used as the session type, this parameter points to a module to use for DBM support, such as gdbm, dbhash, etc.
	</&>

	<&|formatting.myt:param, name="session_id", classname="Session", type="String", users=None &>
	Session id for this session.  When using sessions with cookies, this parameter is not needed as the session automatically creates, writes and retrieves the value from the request.  When using a URL-based method for the session, the id should be retreived from the <&formatting.myt:link, path="session_members", member="id"&> data member when the session is first created, and then used in writing new URLs.
	</&>
	
	<&|formatting.myt:param, name="session_invalidate_corrupt", classname="Session", type="boolean", default="False", users=None &>
	<p>If there are any exceptions upon loading the session, the entire session will be invalidated and started clean.  When object interfaces change in an application, old versions of those objects might still be present in existing session files, and exceptions will be raised when the session object tries to deserialize them into memory.  Setting this to True allows those sessions to be cleaned out and started from scratch again.</p>
	
	<p>This parameter should be used carefully since it can conceal real application errors in certain situations.</p>
	</&>


	<&|formatting.myt:param, name="session_key", classname="Session", type="string", default="myghty_session_id", users=None &>
	The key that will be used as a cookie key to identify sessions.  Changing this could allow several different applications to have different sessions underneath the same hostname.  
	</&>

	<&|formatting.myt:param, name="session_log_file", classname="Session", type="file", users=None &>
	A file or buffer object where debugging information will be sent.
	</&>

	<&|formatting.myt:param, name="session_namespace_class", classname="Session", type="class", users=None &>
	A class that will be used to create the underlying NamespaceManager used by this Session, when a custom NamespaceManager implementation is being used.  By default, the implementation is determined among the built-in NamespaceManagers by the <&formatting.myt:link, param="session_type"&> parameter.  
	</&>

	<&|formatting.myt:param, name="session_type", classname="Session", type="string", default="dbm", users=None &>
	<p>Type of storage used for the session, current types are "dbm" (also called "file"), and "memory".  The storage uses the Container API that is also used by the cache system.
	</p>
	<p>
	When using dbm files, each user's session is stored in its own dbm file, via the class <span class="codeline">myghty.container.DBMNamespaceManager</span> class.  To get the dbm filename used by a session, use <span class="codeline">session.namespace.file.path</span>, or to retrieve a list of the actual files created by the particular dbm instance, use <span class="codeline">session.namespace.file.get_filenames()</span>.
	
	</p>
	</&>

	<&|formatting.myt:param, name="session_secret", classname="Session", type="string", users=None &>
	Secret key to enable encrypted session ids.  When non-None, the session ids are generated with an MD5-signature created against this value.
	</&>

	<&|formatting.myt:param, name="session_timeout", classname="Session", type="integer", users=
	None &>
	Time in seconds before the session times out.  A timeout occurs when the session has not been loaded for more than timeout seconds.
	</&>

	<&|formatting.myt:param, name="session_use_cookies", classname="Session", type="boolean", default="True", users=None &>
	Whether or not to store and retrieve the session ID from the cookies present in the request.  If False, the session ID must be present in the argument list to retrieve an existing session.
	</&>

	<&|formatting.myt:param, name="use_modpython_session", classname="ApacheHandler", type="boolean", users=None &>
	Instructs the get_session() method, or the global variable <i>s</i> if configured, to return an instance of the mod_python session object instead of the Myghty session object.  If this is configured, only the <&formatting.myt:link, param='session_timeout'&> parameter is supported.
	</&>

	<&|formatting.myt:param, name="use_session", classname="ApacheHandler,CGIHandler", type="boolean", users=None &>
	Establishes the global variable <i>s</i> as a reference to the Session object.  This means all requests will automatically have the session initialized and loaded.  If an application has a lot of templates that dont have use for the session, this could add unnecessary overhead.
	</&>


	</&>
</&>

<&|doclib.myt:item, name="methods", description="Session Methods", &>
	<&|formatting.myt:paramtable&>

	<&|formatting.myt:function_doc, name="delete", args=[] &>
	deletes the persistent storage for this session, but the session remains valid.  When save() is called, the new data will be written.
	</&>
	<&|formatting.myt:function_doc, name="invalidate", args=[] &>
	invalidates this session, creates a new session id, returns to the is_new state
	</&>
	<&|formatting.myt:function_doc, name="load", args=[] &>
	Loads the data from this session from persistent storage and updates the last modified time of the session.  This method is called automatically upon session object construction and does not need to be called explicitly.  If the session's persistant storage does not exist, it will be created.  If the session has not been accessed since the timeout period, the invalidate() method will be called, and the session will return to the is_new state, as well as was_invalidated.
	</&>
	<&|formatting.myt:function_doc, name="lock", args=[] &>
	Locks this session against other accesses.  This method is called automatically by the load() and save() methods.  However, this method can be called to keep the session locked persistently until explicitly unlocked by the unlock() method.
	</&>
	<&|formatting.myt:function_doc, name="unlock", args=[] &>
	Unlocks this session against other accesses.  This method is called automatically by the load() and save() methods.  However, this method can be called to unlock a persistent lock set up by the lock() method.
	</&>
	<&|formatting.myt:function_doc, name="save", args=[] &>
	Saves the data for this session to persistent storage.  This should be called whenever you know the session has been modified.
	</&>

	</&>
</&>

<&|doclib.myt:item, name="members", description="Session Members", &>
	<&|formatting.myt:paramtable&>

	<&|formatting.myt:member_doc, name="accessed", &>
	The last time this session was accessed.
	</&>

	<&|formatting.myt:member_doc, name="created", &>
	The time this session was created.
	</&>

	<&|formatting.myt:member_doc, name="id", &>
	<p>The id for this session.  When using cookies, this is retrieved and set within the cookie referenced by the <&formatting.myt:link, param="key"&> string.  The id is automatically created when a new session is instantiated.</p>
	<p>
	When regular cookies are used (the default), this value is the same value sent in the session cookie to the client.  When signed cookies are enabled via the <&formatting.myt:link, path="session_options", param="session_secret"&> parameter, this id is MD5 signed against the secret to form the client cookie value.
	</p>
	</&>

	<&|formatting.myt:member_doc, name="is_new", &>
	True if this session was newly created.  This can be because no previous session existed,
	or the session existed but was invalidated, usually due to a timeout.
	</&>

	<&|formatting.myt:member_doc, name="key", &>
	The key used in cookies to set this session's id.  
	</&>
	<&|formatting.myt:member_doc, name="secret", &>
	
	</&>
	<&|formatting.myt:member_doc, name="timeout", &>
	The timeout span of this session.
	</&>
	<&|formatting.myt:member_doc, name="was_invalidated", &>
	True if this session was invalidated upon opening, usually due to a timeout.   <&formatting.myt:link, member='is_new'&> will always be True as well.
	</&>

	</&>
	
</&>


<&|doclib.myt:item, name="object", description="Using the Session Object Standalone", &>
<p>The session object is actually functionally independent of the rest of Myghty, and is compatible with the mod python request object directly, as well as the request emulator used by CGIHandler.  To instantiate it, simply use its constructor as follows:</p>

	<&|formatting.myt:code, syntaxtype="python"&><%text>
		from mod_python import apache
		from myghty.session import Session
		
		def handle(req):
			session = Session(req, data_dir='/path/to/session_dir', key='user_session_id')
	</%text></&>
	
<p>The full constructor signature for the Session object is as follows:</p>
	<&|formatting.myt:code, syntaxtype="python"&><%text>
	Session(request, id = None, use_cookies = True, 
		invalidate_corrupt = False,
		type = None, data_dir = None, 
		key = 'myghty_session_id', timeout = None, 
		secret = None, log_file = None, **params)
	</%text></&>
<p>Note that the parameters are the same as the configuration arguments with the prefix "session_" removed.</p>

</&>

</&>
