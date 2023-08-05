# encoding: latin1
<%flags>inherit='document_base.myt'</%flags>
<&|doclib.myt:item, name="unicode", description="Unicode Support"&>
<p>Since version 1.1, Myghty provides support for writing unicode strings, and for including non-ASCII characters within component source files.</p>

	<&|doclib.myt:item, name="unicode_writes", description="What You Can Give to m.write() (and m.apply_escapes())"&><p>
When unicode support is enabled, you may pass either 
<&|formatting.myt:codeline&>unicode</&> or plain
<&|formatting.myt:codeline&>str</&>s to
<&formatting.myt:link, path="request_methods", method="write", text="m.write()"&>.
<&|formatting.myt:codeline&>Str</&>s will be interpreted according
the Python's system default encoding (as returned by
<&|formatting.myt:codeline&>sys.getdefaultencoding()</&>.
You may also write any other object, in which case the object
will be coerced to unicode by calling 
<&|formatting.myt:codeline&>unicode()</&> before it is output.
There is one exception to this rule: writing a
<&|formatting.myt:codeline&>None</&> generates no output.
</p>
	</&>

	<&|doclib.myt:item, name="magic_comment", description="The Magic Encoding Comment"&><p>
If a myghty component source file contains contains characters other than those in the python system default encoding (as reported by <&|formatting.myt:codeline&>sys.getdefaultencoding()</&> --- usually ASCII), you may so indicate this by placing a magic encoding comment at the top of the file.
The exact syntax of the magic comment is essentially the same as that <a href="http://docs.python.org/ref/encodings.html">used by python</a>, with the added restriction that the '#' which introduces the magic comment must start at the beginning of a line (without leading whitespace.)
</p>
<p>
The magic encoding comment has affects the interpretation of
any plain text in the component source file, and the contents
of any python unicode string literals.   
It does not have any effect on the interpretation of bytes within
python plain str literals.  
In particular, the following is likely to generate a UnicodeDecodeError:
</p>
	<&|formatting.myt:code&><%text>
                # encoding: latin1

                # This is fine:
                Français

                % m.write(u"Français")  # This is fine, too

                % m.write("Français")   # BAD! => UnicodeDecodeError
	</%text></&>
	</&>

	<&|doclib.myt:item, name="output_encoding", description="Controlling the Output Encoding"&><p>
	The output encoding, and output encoding error handling strategy can be specified using the <&formatting.myt:link, path="parameters", param="output_encoding"&> and <&formatting.myt:link, path="parameters", param="encoding_errors"&> configuration parameters.  It can also be changed for a specific request (or portion thereof) by calling the <&formatting.myt:link, path="request_methods", method="set_output_encoding"&> method.
</p>
<p>Choices for the value of <&formatting.myt:link, path="parameters", param="encoding_errors"&> include:</p>
<dl>
    <dt><&|formatting.myt:codeline&>strict</&></dt>
    <dd>Raise an exception in case of an encoding error.</dd>
    <dt><&|formatting.myt:codeline&>replace</&></dt>
    <dd>Replace malformed data with a suitable replacement marker,
        such as <&|formatting.myt:codeline&>"?"</&>.</dd>
    <dt><&|formatting.myt:codeline&>xmlcharrefreplace</&></dt>
    <dd>Replace with the appropriate XML character reference.</dd>
    <dt><&|formatting.myt:codeline&>htmlentityreplace</&></dt>
    <dd>Replace with the appropriate HTML character entity reference,
      if there is one; otherwise replace with a numeric character reference.
      (This is not a standard python encoding error handler.  It is
      provided by the <&|formatting.myt:codeline&>mighty.escapes</&> module.)
    </dd>
    <dt><&|formatting.myt:codeline&>backslashreplace</&></dt>
    <dd>Replace with backslashed escape sequence.</dd>
    <dt><&|formatting.myt:codeline&>ignore</&></dt>
    <dd>Ignore malformed data and continue without further notice.</dd>
</dl>
<p>See the Python <a href="http://docs.python.org/lib/module-codecs.html">codecs</a> documentation for more information on how encoding error handlers work, and on how you can define your own. </p>

<p>Generally, for components generating HTML output, it sufficient to set <&formatting.myt:link, path="parameters", param="output_encoding"&> to <&|formatting.myt:codeline&>'latin1'</&> (or even 'ascii'), and <&formatting.myt:link, path="parameters", param="encoding_errors"&> to <&|formatting.myt:codeline&>'htmlentityreplace'</&>.  (Latin1 is the default encoding for HTML, as specified in <a href="http://www.faqs.org/rfcs/rfc2616.html">RFC 2616</a>.)  
The <&|formatting.myt:codeline&>'htmlentityreplace'</&> error handler replaces any characters which can't be encoded by an HTML named character reference (or a numeric character reference, if that is not possible) so this setting can correctly handle the output of any unicode character to HTML. 
</p>
	</&>

	<&|doclib.myt:item, name="details", description="Other Details"&>
<p>With unicode support enable the return value from 
<&formatting.myt:link, path="request_methods", method="scomp", 
                       text="m.scomp()"&> will be either a
<&|formatting.myt:codeline&>unicode</&> or a
<&|formatting.myt:codeline&>str</&> in the system default encoding.
</p>
<p>Similarly, the input passed to any
<&formatting.myt:link, path="filtering_filtering",
                       text="component output filters"&>
will also be either a
<&|formatting.myt:codeline&>unicode</&> or a
<&|formatting.myt:codeline&>str</&>.
The filter may return any object which is coercable to 
a <&|formatting.myt:codeline&>unicode</&>.
</p>

<p>Output passed to the 
<&|formatting.myt:codeline&>.write()</&> method of component capture buffers
(specified using the 
<&|formatting.myt:codeline&>store</&> argument of
<&formatting.myt:link, path="request_methods", method="execute_component"&>)
will be either a <&|formatting.myt:codeline&>unicode</&> or a
plain <&|formatting.myt:codeline&>str</&>.
(Using a 
<&|formatting.myt:codeline&>StringIO.StringIO</&> buffer should
just work.
Using a
<&|formatting.myt:codeline&>cStringIO.StringIO</&> buffer will
probably not work, as they don't accept unicode input.)
</p>

<p>Output passed to the 
<&|formatting.myt:codeline&>.write()</&> method of subrequest capture buffers
(specified using the 
<&|formatting.myt:codeline&>out_buffer</&> argument of
<&formatting.myt:link, path="request_methods", method="create_subrequest"&>)
will be encoded <&|formatting.myt:codeline&>str</&>s.
The encoding and error strategy, by default, 
will be the system default encoding and 
<&|formatting.myt:codeline&>'strict'</&>
respectively, irrespective of the
<&formatting.myt:link, path="request_members", member="output_encoding"&>
of the parent request.
These can be changed using the 
<&|formatting.myt:codeline&>output_encoding</&> and
<&|formatting.myt:codeline&>encoding_errors</&> arguments of
<&formatting.myt:link, path="request_methods", method="create_subrequest"&>
(or by calling
<&formatting.myt:link, path="request_methods", method="set_output_encoding"&>
on the subrequest.)
</p>
	</&>


	<&|doclib.myt:item, name="disabling", description="Disabling Unicode Support"&><p>
Myghty's unicode support may be disabled by setting the <&formatting.myt:link, path="parameters", param="disable_unicode"&> configuration parameter.
</p>
	</&>

</&>
