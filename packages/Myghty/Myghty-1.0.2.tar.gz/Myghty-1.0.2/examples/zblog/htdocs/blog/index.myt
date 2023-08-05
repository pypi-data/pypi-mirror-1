<%args>
    blog
    loadcomponent = None
    form = None
    commentform = None
    keyword=False
</%args>

<%init>
    if m.comp('/ajax/myghtyjax.myt:init', 
        post = {
            'handler_uri':'/blog/ajax_post/', 
            'exectype':'writedom', 
            'dom_id':'opwindow'
        },
        edit_post = {
            'handler_uri':'/blog/ajax_edit_post/', 
            'exectype':'writedom', 
            'dom_id':'opwindow'
        },
        delete_post = {
            'handler_uri':'/blog/ajax_delete_post/', 
            'exectype':'writedom', 
            'dom_id':'opwindow'
        },
        ): return
</%init>

<& /ajax/myghtyjax.myt:js &>


% if loadcomponent:
    <div class="rightcontrols">
    <A href="/blog/<% blog.id%>/"><% blog.name %></a>
    </div>
% else:
    <div class="rightcontrols">
    <&|/components:securehref, href="/blog/new_post/?blog_id=%s" % blog.id, action=actions.CreatePost(), blog=blog &>New Post</&>

    </div>

    <h2><% blog.name %></h2>
    <p><% blog.description %></p>
% if keyword:
    <span class="medium">Keyword: <% keyword %></span> &nbsp;&nbsp;&nbsp;&nbsp;<a href="/blog/<% blog.id %>/">all posts</a>
%
    <hr/>

%

<& /form:formstatus, form=form &>

<div id="opwindow">
% if loadcomponent:
%   m.comp(loadcomponent, **ARGS)
% else:
    <&SELF:postlist, blog=blog, keyword=keyword&>
%

</div>


<%method postlist>
    <%args>
        blog
        form=None
        keyword=False
    </%args>
% if form:    
    <& /form:formstatus, form=form &>
%
    <&|/data:blogposts, blog=blog, loop=False, keyword=keyword&>
%       posts = m.content_args['posts']
        <ul>
%       for post in posts:
            <li><& views.myt:post_summary, blog=blog, post=post &></li>
%
        </ul>
    </&>
</%method>

