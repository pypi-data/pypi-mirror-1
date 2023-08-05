<%global>
    from zblog.domain.blog import *
</%global>

<%method post_summary>
    <%args>
        post
        blog
    </%args>
    <h3><% post.headline %></h3>
    <p><% post.summary %></p>

    <div class="rightcontrols">
    <&SELF:post_topics, post=post, blog=blog &><br/>
    Posted <% post.datetime %> by <% post.user.fullname %>
    </div>

    <a href="/blog/view/<% post.id %>/">More...</a>
    <br/>

    <a href="/blog/view/<% post.id %>/#comments">Comments (<% str(post.comment_count) %>)</a>

</%method>

<%method post_topics>
    <%args>
        post
        blog
    </%args>
% sep = ''

% for topic in post.topics:
<% sep %><a href="/blog/<% blog.id %>/topic/<% topic.topic.keyword %>/"><% topic.topic.keyword %></a>\
%   sep = ', '
%

</%method>

<%method view_post>
    <%args>
        post
    </%args>
    <div class="postheader">
    <span class="medium"><% post.headline %></span> 
    &nbsp;&nbsp;&nbsp;&nbsp;<&views.myt:post_controls, post=post&>
    <br/><& SELF:post_topics, post=post, blog=post.blog&>
    <p><% post.summary %></p>
    </div>
    
    <div class="postbody">
    <% post.body %>    
    </div>
</%method>

<%method post_controls>
    <%args>
    post
    </%args>
    <&|/components:securehref, href="javascript:edit_post({'post_id':'%s'})" % post.id, action=actions.EditPost(), post=post &>Edit</&>
    <&|/components:securehref, href="javascript:delete_post({'post_id':'%s'})" % post.id, action=actions.EditPost(), post=post &>Delete</&>
</%method>

<%method view_comment>
    <%args>
        comment
        showpost=False
    </%args>
    <b><% comment.subject %></b>
% if showpost:
    &nbsp;&nbsp;&nbsp;&nbsp;posted to <a href="/blog/view/<% comment.post.id %>/"><% comment.post.headline %></a>
%
% if comment.parent:
    <br/>in reply to <a href="/blog/comments/view/<% comment.parent.id %>/"><% comment.parent.subject %></a>
%
    <br/>
    <% comment.body %>
    <br/>
    Posted by <% comment.user.fullname %> on <% comment.datetime %>
    <a href="/blog/comments/view/<% comment.id %>/#reply">reply</a>
</%method>
