<%flags>
	# specify a layout file to inherit from
	inherit = 'layout.myt'
</%flags>

<&|SELF:section, name='title' &>
	Myghty Really Advanced Layout Demo
</&>

<&|SELF:section, name='header' &>
	<h3>Abstracted Layout Demo - Main Layout</h3>
</&>

<&|SELF:section, name='body' &>
	<p>
	In this example, the autohandler calls upon <i>m</i> to fetch both its immediate subclass
	and the subclass of that subclass.   The "sub-sub-class", which represents
	the ultimate file being served, is called 
	to populate the content dictionary first.  
	Then the "subclass", which defines the layout, is called
	with the newly populated content dictionary as its arguments, which it
	references via the %ARGS section.
	</p>
	<p>This allows pages to select their own layout component, and
	also makes the creation of new layouts easy as they contain virtually
	no python code except straight variable substitutions.   
	With layout and content in separate templates, brought together by 
	the autohandler, the design is extremely close to the "model-view-controller"
	paradigm.
	</p>
	<p>	
	<a href="another.myt">View a page using Layout 2</a>
	</p>
</&>

<&|SELF:section, name='leftnav' &>
	Left Nav <br/><br/>
	<a href="another.myt">View Layout 2</a><br/><br/>
</&>


<&|SELF:section, name='footer' &>

 <& toolbar.myt &>

</&>
