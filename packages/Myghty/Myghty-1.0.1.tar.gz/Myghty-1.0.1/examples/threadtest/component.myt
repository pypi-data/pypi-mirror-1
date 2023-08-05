<%flags>inherit = None</%flags>
<%python scope="global">
	import os,time
	try:
		import thread as thread
	except:
		import dummy_thread as thread
</%python>
<%python scope="thread">
	origpid = os.getpid()
	origid = thread.get_ident()
	modulus = Value()
	counter = Value(0)
</%python>
<%args>
	responsetime = 0
</%args>

% now = int(time.time())
% t = now - int(responsetime)
% counter(counter() + 1)

counter : <% counter() %><br/>
time: <% t %><br/>
orig prod id: <% origpid %><br/>
orig thread id: <% origid %><br/>
current proc id: <% os.getpid() %><br/>
current thread id: <% thread.get_ident() %><br/>

<script>setTimeout('window.location.href="component.myt?responsetime=<% now %>"', 100)</script>
