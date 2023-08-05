<%doc>a hypothetical toolbar</%doc>


<%global>
	import os
</%global>

<a href="/">Demo Server Home</a>

&nbsp; | &nbsp;

<a href="/doc/">Documentation</a>

&nbsp; | &nbsp;

<a href="http://www.myghty.org/">www.myghty.org</a>

&nbsp; | &nbsp;

<a href="/source<% os.path.dirname(r.path_info) %>/">View Source of This Section</a>
