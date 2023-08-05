<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="specialtempl", description="Special Templates", &>
	<&|doclib.myt:item, name="autohandler", description="autohandler", &>
	<P>an autohandler is an optional file, by default named <&|formatting.myt:codeline&>autohandler</&>, that will serve as the base inheriting template for all requests within a directory and its subdirectories.  Inheritance is discussed in more detail in the section <&formatting.myt:link, path="inheritance", text="Inheritance"&>.  The basic idea is that the autohandler template executes first; it runs some code and/or outputs some HTML, and then calls a special method to deliver the content of the requested template.  When the embedded template has completed its execution, the autohandler can then output some more HTML at the bottom and/or execute cleanup code:</p>
	
	<&|formatting.myt:code&><%text>
		<html>
		<head>autohandler demo</head>
		<body>
		% m.call_next()
		</body>
		</html>
	</%text></&>
	<p>Autohandlers are searched for first in the current directory, then upwards in the enclosing directories, until the component root is reached.  If more than one autohandler is found, they will all be executed within each other, with the most directory-specific autohandler executed at the innermost level.  Any page or autohandler can deny the execution of an enclosing autohandler by setting the "inherit" flag to be None.</p>
	<p>Autohandlers are ideal for standardized HTML enclosing schemes as above.  There are also many more creative uses.  An autohandler that automatically protects a whole directory based on a custom login scheme would look something like this:</p>
	
	<&|formatting.myt:code&><%text>
	# autohandler

	<%python scope="init">
		# look in the apache request for some kind of 
		# login token
		user = login_manager.check_login(r)
		if not user:
			# redirect out of here, the rest of the content
			# in this page will not be sent
			m.send_redirect("/login.myt", hard=True)

		else:				
			# otherwise, they are ok, deliver content
			m.call_next()
	</%python>

	</%text></&>
	
	</&>
	<&|doclib.myt:item, name="dhandler", description="dhandler", &>
	<p>A dhandler, otherwise known as a directory handler, is a file, by default named <&|formatting.myt:codeline&>dhandler</&>, that serves requests for which the requested Myghty template can not be located, or for a request that names a directory by itself without a file.  dhandlers are searched for similarly to autohandlers, i.e. in the innermost enclosing directory first, then upwards towards the component root.  However, only one dhandler is executed at a time.  The code within the dhandler has access to the request member <&formatting.myt:link, path="request_members", member="dhandler_path" &> which refers to the path information for the requested (but unlocated) component, relative to the path of the current dhandler.  It also can call  <&formatting.myt:link, path="request_methods", method="decline"&> which will abort the current dhandler and search up the directory tree for the next enclosing dhandler.</p>
	
	<p>Dhandlers are good for special path-based requests used in places such as news sites who want to have clean URLs that have no query strings, for writing components that process the contents of a directory dynamically, such as image or filesystem browsers, or custom per-directory "file not found" handlers.</p>
	

	<p>Example: content management system.  A lot of news sites have fancy URLs with dates and article keywords (sometimes called slugs) specified within them.  These URLs sometimes are resolved into database parameters, and the actual content is retrieved from some source that is not the same as a local file with that path scheme.  This example extracts tokens from a URI and uses them as parameters to retrieve content.</p>
	
	<&|formatting.myt:code&><%text>
	# Hypothetical URL:
	# http://foonews.com/news/2004/10/23/aapl.myt
	
	# dhandler, inside of the web directory /news/

	<%python scope="init">
		import re
		
		# get path
		path = m.dhandler_path
		
		# get arguments from the path
		match = re.match(r"(\d+)\/(\d+)\/(\d+)\/(\w+)\.myt", path)
		
		if match:
			(year, month, day, slug) = match.groups()
			
			# look up a news article in a 
			# hypothetical content-management database 
			# based on this parameters from the path
			article = db.lookup(year, month, day, slug)
		else:
			article = None
			
		if article is None:
			# improper URL, or no article found
			m.send_redirect("article_not_found.myt", hard=False)
	</%python>
	
	<!-- display the article -->
	
	<h3><% article.get_headline() %></h3>
	
	<% article.get_text() %>
	
	</%text></&>

	<p>The tricky part about a dhandler in conjunction with Apache is that the URL used to access the dhandler has to be identified by apache as a Myghty request.  For a basic setup that associates *.myt with Myghty files, the URL used to access the dhandler would have to end with the string ".myt".  To call dhandlers more flexibly, you would have to insure that Apache is configured to send all requests for a particular directory to Myghty for processing, using a directive like DirectoryMatch or FilesMatch.</p>


	</&>

	<&|doclib.myt:item, name="modulecomponents", description="Using Module Components for autohandler/dhandler", &>
	<p>First described in <&formatting.myt:link, path="modulecomponents"&>, these components can also be used as autohandlers or dhandlers.  Simply configure the Myghty environment to recognize paths with "autohandler" and/or "dhandler" as module component paths:</p>

	<&|formatting.myt:code, syntaxtype="python"&><%text>
		module_components = [
			# configure the root autohandler to resolve to Autohandler class
			{r'/autohandler$' : 'modcomp:Autohandler'},
			
			# configure all dhandlers to resolve to Dhandler class
			{r'.*/dhandler$' : 'modcomp:Dhandler'},
		]
	</%text></&>
	
	<p>
	In particular, code-intensive autohandlers and dhandlers such as content delivery mechanisms, translation components, or authentication controllers would be suitable as module components.   Also see the section <& formatting.myt:link, path="resolver" &> for more information on the resolution of autohandlers and dhandlers.
	</p>
	
	</&>
</&>


