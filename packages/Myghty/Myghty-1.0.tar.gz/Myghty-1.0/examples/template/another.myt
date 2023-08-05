<%flags>
        # specify a layout file to inherit from
        inherit = 'layout2.myt'
</%flags>


<&|SELF:section, name='title' &>
	Myghty Advanced Layout Demo - Page 3
</&>

<&|SELF:section, name='header' &>
	<h3>Abstracted Layout Demo - Layout 2</h3>
</&>

<&|SELF:section, name='body' &>
	<p>
	This is another page using a different layout.  
	
	</p>


</&>

<&|SELF:section, name='leftnav' &>
	this is the left nav<br/><br/>
	<a href="index.myt">Back to Layout 1</a>
</&>


<&|SELF:section, name='footer' &>

 <& toolbar.myt &>

</&>
