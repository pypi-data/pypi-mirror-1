<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="otherblocks", description="Other Blocks", &>
	<p>Myghty has some miscellaneous <% "<%xxxx>" %> blocks, whose contents are less than pure Python.  The most important is the <% "<%flags>" %> section, since it controls several important behaviors of a component.</p>
	
	<&|doclib.myt:item, name="flags", description="<%flags>", escapedesc=True &>
	<p>%flags is used to specify special properties of the component, which are significant to the execution of the component in the Myghty environment.  Some flags can be inherited from a parent supercomponent, and overridden as well.  Current flags are:</p>

	<ul>
		<li><p> <&|formatting.myt:codeline&>inherit = "/path/to/template"</&> - used in a file-based component only, this flag indicates that this component should inherit from the given template file.  This argument can also be None to indicate that this component should not inherit from anything, even the standard autohandler.  This flag only applies to the component file that it appears in, and does not affect any super- or subclass components.   See the section <&formatting.myt:link, path="inheritance", text="Inheritance"&> for details.
		</p>
		<li> <p><&|formatting.myt:codeline&>autoflush = [True|False]</&> - will override the configuration parameter <&|formatting.myt:codeline&>auto_flush</&> for this individual component.  This is mostly useful for a particularly large top-level component, or a filter component that requires the full output text in one chunk.  When a comopnent has autoflush disabled, it essentially means that a buffer is placed between the component's output and the ultimate output stream.  As a result, the delivery of any component within a buffered component is also going to be buffered - this includes when a superclass component calls <&|formatting.myt:codeline&>m.call_next()</&> or for any subcomponent or method call.</p>
		<p>
		This flag is also inherited from a superclass component, such as the autohandler.  See the section <&formatting.myt:link, path="filtering_autoflush", &> for information on auto_flush.
		</p>
		<li> <p><&|formatting.myt:codeline&>trim = ["left"|"right"|"both"]</&> - provides automatic left and/or right whitespace trimming for the output of a component.  This is the equivalent of a <% "<%filter>" %> section utilizing <&|formatting.myt:codeline&>string.strip()</&> combined with <&|formatting.myt:codeline&>autoflush=False</&>.  This allows component source code to be laid out on multiple lines without the whitespace surrounding the component output being presented in the final output.  For information on trim, see the section <&formatting.myt:link, path="filtering_filtering_trim", &>.</p>
		
		<li><p><&|formatting.myt:codeline&>use_cache</&> - Enables caching for the component.  See <&formatting.myt:link, path="caching"&> for further cache options.
	</p>
	<li><p><&|formatting.myt:codeline&>encoding = ["utf-8" | "latin-1" | etc ]</&> - Specifies the character encoding of the component's text file (such as utf-8, etc.).  This encoding goes directly to the Python "magic comment" at the top of the generated Python component, so any character set is supported by Myghty templates. 
	</p>
	<li><p><&|formatting.myt:codeline&>persistent = [True|False]</&> - overrides the per-interpreter setting of <&formatting.myt:link, path="params", param="delete_modules"&> to specify that this file-based component should or should not specifically have it's module removed from sys.modules when it has fallen from scope.  A file-based component that contains class definitions which may remain active after the component itself has fallen out of use may want to do this.</p>
	</ul>
	<p>Flags may be specified via the <% "<%flags>" %> tag, or for subcomponents and methods may be specified as inline attributes within the <% "<%def> or <%method>" %> tags.  The <% "<%flags>" %> tag may appear anywhere in a component, or even across multiple %flags sections, and will still take effect before a component is actually executed.</p>
	
	<p>Example: the <% "<%flags>"%> tag:</p>
	<&|formatting.myt:code&><%text>
		<%flags>
			inherit = None
			autoflush = True
		</%flags>
		
		<%python scope="init">
			...
		</%python>
	</%text></&>

	<p>Example: subcomponent flags as attributes:</p>
	<&|formatting.myt:code&><%text>
		<%method getlink trim="both">
			<%init>
			</%init>
			
			<A href="foo.bar">lala</a>
		</%method>
	</%text></&>
		
	

	</&>
	<&|doclib.myt:item, name="attr", description="<%attr>", escapedesc=True &>
	<p>%attr simply sets some attributes on the component.  These attributes are accessed via the <&formatting.myt:link, path="components_members", member="attributes"&> member of the component.  Below, two attributes are accessed from a component to provide style information.  One uses <& formatting.myt:link, path="request_members", member="current_component"&>, and the other uses <& formatting.myt:link,  path="request_members", member="base_component"&>.  The difference is the former always returns the very same component that is currently executing, whereas the latter corresponds to the component at the bottom of the inheritance chain:</p>
	<&|formatting.myt:code&><%text>
	<%attr>
		bgcolor = "#FF0000"
		fgcolor = "#FA456A"
	</%attr>
	
	<style>
		body {
		background-color: <% m.current_component.attributes['bgcolor'] %>;
		text-color: <% m.base_component.attributes['fgcolor'] %>;
		}		
	</style>
	
	# ...
	</%text></&>
	<p>In both cases, if the attribute does not exist in the current component or within futher inheriting child components, it will then traverse upwards via parent components to locate the attribute.  For more information on parent/child relationships between components, see the section <&formatting.myt:link,path="inheritance"&>.  </p>
	</&>
	
	<&|doclib.myt:item, name="text", description="<%text>", escapedesc=True &>
	<p>%text surrounds a block where Myghty will not parse for control lines, line comments, substitutions, or any other Myghty tag.  This allows the placement of free text which is intended to print as is, even if it may contain characters that are normally significant to the Myghty lexer.   The %text tag is also essential for writing documentation that illustrates examples of Myghty (or similar) code.</p>
	</&>
	<&|doclib.myt:item, name="doc", description="<%doc>", escapedesc=True &>
	<p>%doc is simply a comment string - the content inside of a <% "<%doc>" %> section is discarded upon compilation.  Comments can also be stated on a per-line basis using a '#' character as the very first character on a line, as described in <&formatting.myt:link, path="embedding_comment" &>.</p>
	</&>
</&>



