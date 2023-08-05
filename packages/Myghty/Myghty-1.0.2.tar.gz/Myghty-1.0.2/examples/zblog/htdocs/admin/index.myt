<%init>    
    if m.comp('blog.myt:ajax') or m.comp('user.myt:ajax'): return
</%init>

<& /ajax/myghtyjax.myt:js &>

<h3>ZBlog Management</h3>

<ul>
    <&|blog.myt:links&>
        <li><a href="<% m.content_args['url'] %>"><% m.content_args['text'] %></a></li>
    </&>
    <&|user.myt:links&>
        <li><a href="<% m.content_args['url'] %>"><% m.content_args['text'] %></a></li>
    </&>
</ul>

<div id="opwindow">
</div>

