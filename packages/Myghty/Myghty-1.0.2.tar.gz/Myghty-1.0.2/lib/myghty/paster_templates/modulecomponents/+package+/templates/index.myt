<%attr>
	context='home'
	title="Welcome to Module Components"
</%attr>

<div class="main">
welcome to the slightly more complicated myghty app !

<p>This template illustrates a simple controller setup, including a login page, and a context-sensitive navigation bar.</p>

<p>The page you are viewing is "templates/index.myt".  It works similarly to index.myt inside the "myghty_simple" template; the page is "wrapped" by an autohandler file, "components/autohandler", and the autohandler pulls in "components/header.myc", "components/footer.myc" and "components/leftnav.myc" to create the finished page.   
</p>

<p>
However, unlike the myghty_simple setup, every request is served by a controller module, which is "lib/controller.py".  Path names in the URL are mapped to individual method names upon one or more object instances inside the controller via the ResolvePathModule resolver rule.  Each controller forwards onto an ".myt" template for display.
</p>

<p>
The directories laid out for this approach are:
<ul>
	<li><b>lib/</b> - stores Python modules, including controller modules that handle requests.  Currently there is just one module, "controller.py", which contains one controller object, an instance of a class named "SimpleController".  SimpleController has two methods, one for the homepage and one for the login system.  While this is a very simple setup, there can be any number of controller modules, objects, and methods.</li>
	<li><b>templates/</b> - stores .myt templates which are	invoked by controller modules.  These templates also can include a context attribute at the top, which gives a clue to the left navigation bar about the currently displaying page, as well as a title attribute, which overrides the titlebar text set up by the autohandler.</li>
	<li><b>components/</b> - stores .myc components, which are components used by the templates.  ".myc" vs. ".myt" is just a naming convention that makes it easier to distinguish between top-level templates and smaller components.</li>
	<li><b>htdocs/</b> - stores all static content, such as .css, .png, etc.  The Myghty interpreter doesn't even know about /htdocs, as static content is handled by the underlying Paste server (or whatever static webserver is being used).</li>
</ul>
</p>
<p>Note that by keeping all templated files in a different set of directories than the static directory, there is no chance of a templated file ever being served "raw" by the webserver.
</p>

</div>

