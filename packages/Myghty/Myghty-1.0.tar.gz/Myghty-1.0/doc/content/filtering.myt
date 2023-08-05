<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="filtering", description="Filtering and Flushing (and Escaping)", escapedesc=True, header="Additional Features" &>

<p>This section describes some options that can be applied to Myghty components which affect how the request object deals with their output.   The request object supports the capturing of component output in a buffer which is flushed upon completion to provide simple and flexible component output behavior, or sending the output directly to the underlying output stream to provide faster perceived response time.  This option is known as <b>autoflush</b>.   Post-processing functions can be attached to the final output of a component at the top-level or callable component level, allowing user-defined text operations on the output, known as <b>filtering</b>.  Autoflushing and filtering have some dependencies on each other, so they are described together.</p>

<p>As a convenient alternative to filtering, common text-escaping functions applicable to a web application environment, plus support for user-defined escape functions, are provided under the functionality of <b>escapes</b>, described at the end of the section.</p>

<&|doclib.myt:item, name="autoflush", description="The Autoflush Option", escapedesc=True &>
<p>The <&|formatting.myt:codeline&>autoflush</&> option controls whether the output of a component is sent to the underlying output stream as it is produced, or if it is first captured in a buffer which is then sent in one chunk at the end of the request's lifecycle.  This is significant in a web context, as it affects "perceived performance", which means the response time of an unbuffered page is nearly immediate, even though the time it takes to finish might be the same as that of a buffered page.</p>

<P>While the autoflush option can improve perceived performance, there are also increased complexities with an autoflushed, i.e. unbuffered page.  HTTP headers, including hard redirects, must be sent before any content is written, else the response will have already begun and any new headers will simply be displayed with the page's content.   A soft redirect, not being dependent on HTTP headers, will still function, but it's output also may be corrupted via any preceding output.  Error messages also will appear inline with already existing content rather than on a page of their own.</p>

<p>
The option can be set for an entire application, for a set of files or directories via autohandlers/inherited superpages, for an individual page, or even an individual method or subcomponent within a page.   Within all of those scopes, the flag can be set at a more specific level and will override the more general level.  </p>

<p>With no configuration, the parameter defaults to <&|formatting.myt:codeline&>False</&>, meaning that component output is captured in a buffer, which is flushed at the end of the request or subcomponent's execution.  This produces the simplest behavior and is fine for most applications.</p>

<p>But, here you are and you want to turn <&|formatting.myt:codeline&>autoflush</&> on.  To set it across an entire application, specify <span class="codeline">autoflush=True</span> to the Interpreter or HTTPHandler being used.  Or to configure via http.conf with mod_python:</p>

<&|formatting.myt:code&>
	PythonOption MyghtyAutoflush True
</&>

<p>When autoflush is true for an entire application, no buffer is placed between the output of a component and the underlying request output stream.  The flag can be overridden back to <&|formatting.myt:codeline&>False</&> within directories and pages via the use of the <&|formatting.myt:codeline&>autoflush</&> flag within the %flags section of the page.  To set the value of autoflush for a particular directory, place an <&|formatting.myt:codeline&>autohandler</&> file at the base of the directory as such:

<&|formatting.myt:code&><%text>
<%flags>autoflush=False</%flags>
% m.call_next()
</%text></&>

<p>The Myghty request will run the autohandler which then calls the inherited page via the <&|formatting.myt:codeline&>m.call_next()</&> call.   The autoflush flag indicates that buffering should be enabled for the execution of this page, overriding the per-application setting of True. </p>

<p>The ultimate <span class="codeline">autoflush</span> flag that is used for a page is the innermost occuring flag within the templates that comprise the wrapper chain.  If no autoflush flag is present, the next enclosing template is used, and if no template contains an autoflush flag, the application setting is used.  Even though an autohandler executes before the page that it encloses, the Myghty request figures out what the autoflush behavior should be before executing any components so that it takes the proper effect.</p>

<p>So any page can control its own autoflush behavior as follows:</p>

<&|formatting.myt:code&><%text>
<%flags>autoflush=False</%flags>
<html>
	<head>
	...
</html>
</%text></&>

<&|doclib.myt:item, name="subcomponents", description="Setting Autoflush in Subcomponents" &>
<p>
Subcomponent or methods can determine their autoflush behavior as follows:
</p>
<&|formatting.myt:code&><%text>
<%def mycomp>
<%flags>autoflush=False</%flags>
	... stuff ...
</%def>
</%text></&>
<p>There is one limitation to the autoflush flag when used in a subcomponent.  If autoflush is set to True on a subcomponent, within a request that has autoflush set to False, the component will send its unfiltered data directly to the output stream of its parent; however since the overall request is not autoflushing and is instead capturing its content in a buffer of its own, the content is still stored in a buffer, which does not get sent to the client until the request is complete.  Note that this limitation does not exist the other way around;  if an overall request is autoflushing, and a subcomponent sets autoflush to False, that subcomponent's output will be buffered,  until the subcomponent completes its execution.  This is significant for a subcomponent whos output is being processed by a <% "<%filter>" %> section.  More on this later.
</p>
</&>

<&|doclib.myt:item, name="autohandlers", description="Non-Buffered with Autohandlers", escapedesc=True  &>
<p>What happens when a page in an autoflush=True environment interacts with one or more autohandlers or inherited superpages?  The superpage will execute first, output whatever content it has before it calls the subpage, and then will call <&|formatting.myt:codeline&>m.call_next()</&> to pass control to the subpage.  If the subpage then wants to play with HTTP headers and/or perform redirects, it's out of luck:</p>

	<&|formatting.myt:code, title="autohandler - autoflush enabled"&><%text>
	<%flags>autoflush=True</%flags>
	<html>
		<head></head>
		<body>
	% m.call_next()
		</body>
	</html>
	</%text></&>

	<&|formatting.myt:code, title="page.myt - wants to send a redirect"&><%text>
	<%python scope="init">
		m.send_redirect("page2.myt", hard=True)
	</%python>
	</%text></&>



<p>The above example will fail!  Since the autohandler executes and prints the top HTML tags to the underlying output stream, by the time page.myt tries to send its redirect, the HTTP headers have already been written and you'll basically get a broken HTML page.   What to do?  Either page.myt needs to specify that it is not an autoflushing page, or it can detach itself from its inherited parent.</p>

<p>Solution One -  Turn Autoflush On:</p>

	<&|formatting.myt:code, title="page.myt"&><%text>
	<%flags>autoflush=False</%flags>
	<%python scope="init">
		m.send_redirect("page2.myt", hard=True)
	</%python>
	</%text></&>

<p>This is the most general-purpose method, which just disables autoflush for just that one page.</p>

<p>Solution Two - Inherit from None</p>

	<&|formatting.myt:code, title="page.myt"&><%text>
	<%flags>inherit=None</%flags>
	<%python scope="init">
		m.send_redirect("page2.myt", hard=True)
	</%python>
	</%text></&>
	
<p>This method is appropriate for a page that never needs to output any content, i.e. it always will be performing a redirect.  The autohandler here is not inherited, so never even gets called.  This saves you the processing time of the autohandler setting up buffers and producing content.  Of course, if there are autohandlers that are performing operations that this subpage depends upon, then you must be sure to inherit from those pages, possibly through the use of "alternate" autohandlers that inherit only from the desired pages.  

</&>
</&>





<&|doclib.myt:item, name="filtering", description="Filtering", escapedesc=True &>
<p>Filtering means that the output stream of a component is sent through a text processing function which modifies the content before it is passed on to the ultimate output stream.   Typical usages of text filtering are modifying entity references, trimming whitespace, converting plain-text to HTML, and lots of other things.  For the general purpose per-component filter, Myghty supplies the <nobr><% "<%filter>" %></nobr> tag.  
</p>


<&|doclib.myt:item, name="filter", description="The <%filter> Tag", escapedesc=True &>
<p>%filter describes a filtering function that is applied to the final output of a component.  This is more common on subcomponents or methods but works within the scope of any top-level component as well.   The Python code within the %filter section provides the body of the to be used; the heading of the function is generated within the compiled component and not normally seen.  The filter function is provided with one argument <i>f</i> which contains the content to be filtered; the function processes content and returns the new value.</p>

<p>Example:</p>

<&|formatting.myt:code&><%text>
<%filter>
import re
return re.sub(r"turkey", "penguin", f)
</%filter>

dang those flyin turkeys !

</%text></&>

<p> will produce:</p>

<&|formatting.myt:code&>
dang those flyin penguins !
</&>	

</&>

<&|doclib.myt:item, name="escapefilter", description="Escaping Content in a Filter Section", escapedesc=True &>
<p>Myghty has some built in escaping functions, described in the next section  <&formatting.myt:link, path="filtering_escaping"&>.  While these functions are easy enough to use within substitutions or any other Python code, you can of course use them within a filter section as well.</p>
<p>This is a component that HTML escapes its output, i.e. replaces the special characters <% "&, <, and >" | h%> with entity reference encoding:</p>

	<&|formatting.myt:code&><%text>
	<%def bodytext>
		<%filter>
			return m.apply_escapes(f, 'h')
		</%filter>

		# ... component output
	</%def>
	</%text></&>

</&>

<&|doclib.myt:item, name="filterflush", description="Filtering Behavior with Autoflush Enabled", escapedesc=True &>

<p>The usual case when a %filter section is used is that all <&|formatting.myt:codeline&>m.write()</&> statements, both explicit and implicit, send their content to a buffer.  Upon completion of the component's execution, the buffer's content is passed through the function defined in the %filter section.  However when autoflush is enabled, the extra buffer is not used and the filtering function is attached directly to each call to <&|formatting.myt:codeline&>m.write()</&>.  For regular blocks of HTML, the entire block is sent inside of one big <&|formatting.myt:codeline&>write()</&> statement, but each python substitution or other code call splits it up, resulting in another call to <&|formatting.myt:codeline&>write()</&>.</p>

<p>Since a non-autoflushing component is more predictable for filtering purposes than an autoflushing component, it is often useful to have autoflush disabled for a component that uses a %filter section.  As stated in the autoflush section, autoflushing behavior can be changed per component, per page or for the whole application, and is the default value as well.   There is also another configuration option 

can be overridden for all filter components by the setting "dont_auto_flush_filters" - see the section <&formatting.myt:link, path="parameters", &> for more information.</p>

</&>

<&|doclib.myt:item, name="trim", description="Filtering Whitespace - the Trim Flag", escapedesc=True &>
<p>A common need for components is to trim off the whitespace at the beginning and/or the end of a component output.  It is convenient to define subcomponents and methods on multiple lines, but this inherently includes newlines in the output of that component, since Myghty sees the blank lines in the source.  But lots of times the ultimate output of a component needs to not have any surrounding whitespace, such as a component that outputs a hyperlink.  While a regular %filter section can be used for this, Myghty provides the <&|formatting.myt:codeline&>trim</&> flag, as so:</p>

	<&|formatting.myt:code &><%text>
	for more information, click <&makelink, a="here", p=4.3, xg="foo" &>.
	
	<%def makelink trim="both">
	<%args>
		p
		xg
		a
	</%args>
	
	<%doc>note this component has a lot of whitespace in it</%doc>
	<A href="http://foo.myt?xg=<% xg %>&p=<% p | u %>"><% a %></a>
	
	</%def>
	</%text></&>

	<p>Output:</p>
 	<&|formatting.myt:code &><%text>
	for more information, click <A href="http://foo.myt?xg=foo&p=4.3">here</a>.
	</%text></&>
	<p><&|formatting.myt:codeline&>trim</&> supports the three options <&|formatting.myt:codeline&>left</&>, <&|formatting.myt:codeline&>right</&>, or <&|formatting.myt:codeline&>both</&>, trimming whitespace on the left, right and both sides of component output, respectively.
	</p>
</&>

</&>


<&|doclib.myt:item, name="escaping", description="Escaping Content", escapedesc=True &>

<p>Escaping usually refers to a kind of filtering that converts the characters in a string into encoded values that can be safely passed through other character-parsing systems without them interfering.</p>

<p>Myghty provides built in support for HTML and URL escaping (also called URL encoding), and has plans for entity-reference escaping.  User-defined escape functions can be added to an application as well.
</p>

<&|doclib.myt:item, name="substitutions", description="Escaping Substitutions", escapedesc=True &>

<p>Substitutions, first introduced in <&formatting.myt:link, path="embedding_substitutions"&>,  can include escape flags, specified by the following notation:</p>

	<&|formatting.myt:code &><%text> 
	<% "i am an argument" | u %> 
	</%text></&>

<p>The above example will URL encode the embedded string.  The two escape flags included with Myghty are "u" for url encoding, and "h" for HTML encoding.    Entity reference encoding is in the works.</p>

<p>Multiple escape flags are separated by a comma:</p>

	<&|formatting.myt:code &><%text> 
	<% "multiple escapes" | h, u %> 
	</%text></&>

<p>Which will HTML and URL escape the given string.</p>

</&>


<&|doclib.myt:item, name="programmatic", description="Programmatic Escaping", escapedesc=True &>

<p>The HTML and URL-encoded escaping functions described above are easy enough to use programmatically as well.  The request object provides the escaping functions via the <&|formatting.myt:codeline&>apply_escapes()</&> method for this purpose.  This method uses the same flags as an escaped substitution, the defaults being "h" for HTML escaping and "u" for URL encoding.</p>

<p>In this example, a component receives the argument "text" and displays it in a textarea, where HTML escaping is required:</p>

<&|formatting.myt:code&><%text>
	<%args>
		text
	</%args>
	<%python>
		# HTML escape the given text
		text = m.apply_escapes(text, 'h')
	</%python>

	<textarea><% text %></textarea>
</%text></&>

<p>The first argument to <&|formatting.myt:codeline&>apply_escapes()</&> is the text to be escaped, and the second is a list of escape flags.  Since strings are lists in Python, multiple flags can be specified either in a single string as in <&|formatting.myt:codeline&>"hu"</&> or as a regular list such as <&|formatting.myt:codeline&>['h', 'u']</&>.

</&>

<&|doclib.myt:item, name="custom", description="Custom Escape Flags", escapedesc=True &>
<p>You can add your own escape flags to your application via the <&|formatting.myt:codeline&>escapes</&> configuration parameter.  <&|formatting.myt:codeline&>escapes</&> is in the form of a dictionary, with the key names being the single-character escaping token and the values being function pointers to escaping functions.</p>

<p>In this example, an escape flag 'p' is added which provides the ability to convert the word "turkey" into "penguin":

<&|formatting.myt:code&><%text>
    escapes = {
        'p':re.sub('turkey', 'penguin', f)
    }
</%text></&>

</&>



<&|doclib.myt:item, name="custom", description="Default Escape Flags", escapedesc=True &>

<p>Default escaping can be configured via the configuration parameter <&|formatting.myt:codeline&>default_escape_flags</&> (PythonOption MyghtyDefaultEscapeFlags).  The format of this parameter is a list of escape flag characters.  This applies the given flags to <b>all</b> substitutions in an application.</p>

<p>When default escaping is used, the special flag "n" can be specified in the substitution to disable the default escape flags for that substitution.</p>
</&>



</&>




</&>
