<%args>
	call_type = None
</%args>
<%python scope="init">
</%python>

<h3>/examples/components/index.myt</h3>

<form method="post" action="index.myt">
	
	Select the type of component call you would like.
	Press "submit" to enact the call upon the template "component.myt".
	<br/><br/>

	<input type="radio" name="call_type" value="" <% not call_type and 'checked' or '' %>>None<br/>
	<input type="radio" name="call_type" value="plain" <% call_type == 'plain' and 'checked' or '' %>>Plain<br/>
	<input type="radio" name="call_type" value="subrequest" <% call_type == 'subrequest' and 'checked' or '' %>>Subrequest<br/>
	<input type="radio" name="call_type" value="soft" <% call_type == 'soft' and 'checked' or '' %>>Soft Redirect<br/>
	<input type="radio" name="call_type" value="hard" <% call_type == 'hard' and 'checked' or '' %>>Hard Redirect<br/>
	<input type="submit">
</form>

<div style="border:1px solid;margin:20px;padding:10px;">
<%python>
	if call_type=='plain':
		m.comp('component.myt')
	elif call_type=='subrequest':
		m.subexec('component.myt')
	elif call_type=='soft':
		m.send_redirect('component.myt', hard=False)
	elif call_type=='hard':
		m.send_redirect('component.myt', hard=True)
	else:
		m.write("didnt call component")
</%python>
</div>

<%method title>
Myghty Examples - Component Calling
</%method>
