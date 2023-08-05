<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="embedding", description="Embedding Python in HTML", header="The Myghty Environment" &>
<p>A Myghty file usually is laid out as an HTML file, or other text file, containing specialized tags that are recognized by the Myghty page compiler.  When compiled, the file is converted into a python module which is then executed as regular python code.  A Myghty template in its compiled form is typically referred to as a <i>component</i>.  A <i>component</i> can also contain one or more <i>subcomponents</i> and/or <i>methods</i>, which are described further in the section <&formatting.myt:link, path="components", text="Components"&>.  Basically when we say "component" we are talking about a self contained unit of Myghty templating code.  The term "top level component" refers to the outermost component within a request, which is the page itself being executed.  The term "file based component" refers to a component corresponding to the file that it appears in.
</p>
	<&|doclib.myt:item, name="control", description="Control Lines", &>
	<p>Control lines look like this:</p>
	<&|formatting.myt:code &>
	<%text>
	% for x in range(0, 10):
		hello!<br/>
	% # end for
	</%text>
	</&>

	<p>The percent sign must be the very first character on the line, and the rest of the text is interpreted directly as Python code.   The whitespace of the line, as well as the presence of a colon at the end of the line, is significant in determining the indentation of subsequent, non-control lines.  As in the example above, the "for" statement followed by a colon, sets the indentation to be one level deeper, which causes the html text "hello!" to be iterated within the block created by the Python statement.  The block is then closed by placing another control line, containing only whitespace plus an optional comment.</p>
	
	<p>A more involved example:</p>
	<&|formatting.myt:code &><%text>
	% for mood in ['happy', 'happy', 'sad', 'sad', 'happy']:
	%	if mood == 'happy':
	
	  <img src="happyface.gif"/> Hey There !
	
	% 	else:
	
	  <img src="sadface.gif"/> Buzz Off !
	
	% #if statement
	% #for loop
	</%text>
	</&>
	
	<p>Note that the whitespace is not significant in plain HTML or text lines.  When this template is converted to Python code, the plain text will be embedded in <&|formatting.myt:codeline&>write</&> statements that are indented properly within the block.  Block-closing statements like "else:" and "except:" are also properly interpreted.</p>

	</&>
	<&|doclib.myt:item, name="comment", description="Comment Lines", &>
	<p>
	Note that a blank control line, i.e. starting with '%', is significant in affecting the whitespace indentation level, whether or not it contains a comment character '#' followed by a comment.  To do line-based comments without affecting whitespace, use '#' as the very first character on a line:
	</p>
	<&|formatting.myt:code &><%text>
	% for x in (1,2,3):
		<b>hi <% x %></b>

	# a comment

	% # a block-closing control line
	</%text></&>

	<p>Comments can also be done with the <% "<%doc>" %> tag described in <&formatting.myt:link, path="otherblocks_doc" &>. </p>
	</&>

	<&|doclib.myt:item, name="substitutions", description="Substitutions", &>
	<P>A substitution is an embedded python expression, whos evaluated value will be sent to the output stream of the component via a <&|formatting.myt:codeline&>m.write()</&> statement:</p>
	<&|formatting.myt:code &><%TEXT>
	Three plus five is: <% 3 + 5 %> 
	</%TEXT></&>
	
	<p>produces:</p>
	<&|formatting.myt:code &><%TEXT>
	Three plus five is: 8
	</%TEXT></&>
	
	<p>Substitutions can also span multiple lines which is handy in conjunction with triple-quoted blocks.</p>
	
	<p>The text of substitutions can also be HTML or URL escaped via the use of flags.  For a description of escape flags, see the section <&formatting.myt:link, path="filtering_escaping"&>.
	</p>
	</&>


	<&|doclib.myt:item, name="blocks", description="Python Blocks", &>
	<p>A python block is a block of pure python code:</p>
	<&|formatting.myt:code &><%text>
	<%python>
		user = usermanager.get_user()
		m.write("username is %s" % user.get_name())
	</%python>
	</%text></&>
	<p>Code within a %python block is inserted directly into the component's generated Python code, with its whitespace <b>normalized</b> to that of the most recent control line.  The %python tags, as well as the code within the tags, can be at any indentation level in relation to the rest of the document, including other %python blocks; it is only necessary that the indentation of the code within the block is internally consistent with itself.  See the next section for an example.</p>
	
	<p>
	There are also variations upon the %python block, where the contained Python code is executed within a specific context of a component's execution, such as initialization, cleanup, or global.  These special variations are explained in <&formatting.myt:link, path="scopedpython"&>.
	</p>
	</&>

	<&|doclib.myt:item, name="whitespace", description="Controlling Whitespace with the Backslash", &>
	<p>To allow for finer control of the whitespace inherently generated by multiline HTML or Python control structures, the backslash character "\" can be used at the end of any line to suppress newline generation:
	
	<&|formatting.myt:code&><%text>
		<span class="light">\
		% for x in (1,2,3):
			[<% x %>]\
	 	%
	 	</span>
	</%text></&>
	
	Which will produce:

	<&|formatting.myt:code&><%text>
		<span class="light">[1][2][3]</span>
	</%text></&>
	
	</&>
	
	<&|doclib.myt:item, name="indentation", description="Indentation Behavior", &>
	<p>The interaction of control lines, plain text, and python blocks is regulated by the Myghty engine to create an overall indentation scheme that is functional but also allows HTML and python blocks to be laid out with a high degree of freedom.  The following example illustrates the indentation behavior:</p>
	
	<&|formatting.myt:code &><%text>
	<%python>
		forecasts = {
			'monday':'stormy',
			'tuesday':'sunny',
			'wednesday':'sunny', 
			'thursday':'humid',
			'friday':'tornado'
		}

	</%python>

	% for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:

		<%python>

		weather = forecasts[day]
		if weather == 'tornado':
			advice = "run for the hills !"
		elif weather == 'stormy':
			advice = "bring an umbrella"
		else:
			advice = "enjoy the day...."
		</%python>

	Weather for <% day %>:  <% forecasts[day] %>
	Advice: <% advice %>

	% # end for

	</%text></&>

	<p>The above block, when compiled, translates into the following Python code, that is then executed to produce the final output:</p>
	
	<&|formatting.myt:code, syntaxtype="python" &><%text>
              # BEGIN BLOCK body
              m.write('''
''')
              # test.myt Line 1

              forecasts = {
                      'monday':'stormy',
                      'tuesday':'sunny',
                      'wednesday':'sunny', 
                      'thursday':'humid',
                      'friday':'tornado'
              }


              # test.myt Line 11
              m.write('''
''')
              for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                     # test.myt Line 13
                     m.write('''
	''')
                     # test.myt Line 14


                     weather = forecasts[day]
                     if weather == 'tornado':
                             advice = "run for the hills !"
                     elif weather == 'stormy':
                             advice = "bring an umbrella"
                     else:
                             advice = "enjoy the day...."
                     
                     # test.myt Line 24
                     m.write('''
Weather for ''')
                     m.write( day )
                     m.write(''':  ''')
                     m.write( forecasts[day] )
                     m.write('''
Advice: ''')
                     # test.myt Line 26
                     m.write( advice )
                     m.write('''

''')
                     # test.myt Line 28
              # end for
              # END BLOCK body
	</%text></&>
	
	</&>
	
</&>


