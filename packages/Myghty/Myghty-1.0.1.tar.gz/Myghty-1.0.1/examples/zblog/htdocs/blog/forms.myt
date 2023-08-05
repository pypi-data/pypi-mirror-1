<%method postform>
    <%args>
        form
        blog
        post=None
        preview=None
    </%args>

% if preview is not None:
    <h3>Post Preview</h3>
    <& views.myt:view_post, post=preview &>
    <hr/>
%

% if post is not None:
    <h4>Editing '<% post.headline %>'</h4>
% else:
    <h4>Posting to <% blog.name %></h4>
%    
    <&|/components:entryform, form=form, action="/blog/post/" &>
        <&/components:field, type="hidden", name="preview", value="0"&>
        <&/components:field, type="hidden", name="blog_id"&>
        <&/components:field, type="hidden", name="post_id"&>
        <&|/components:field, type="text", name="headline", size="50"&>
            Headline
        </&>
        <&|/components:field, type="text", name="topic_keywords", size="50"&>
            Topics<br/>
            (separated by spaces)
        </&>
        <&|/components:field, type="textarea", name="summary", rows="3", cols="50"&>
            Summary
        </&>
        <&|/components:field, type="textarea", name="body", rows="10", cols="50"&>
            Body
        </&>
        <&|/components:row, colspan="2"&>
% if post is not None:
            <&/components:field, type="submit", value="Update Post"&>
            <&/components:field, type="button", value="Delete Post", onclick="delete_post({'post_id':'%s'})" % post.id &>
% else:
            <&/components:field, type="submit", value="Post"&>
%            
            <&/components:field, type="button", value="Preview", onclick="document.%s.preview.value=1;document.%s.submit()" % (form.name, form.name)&>
        </&>
    </&>
</%method>


<%method status>
    <%args>
        form
    </%args>
<& /form:formstatus, form=form &>       
</%method>

<%method delete_confirm>
    <%args>
        post
    </%args>
    <&|/components:confirm, yes="delete_post({'post_id':'%s','confirm':1})" % post.id, 
                no="edit_post({'post_id':'%s'})" % post.id&>
    <h3>Delete post '<% post.headline %>'</h3>                
    Are you sure you want to delete this post ?  This will also
    delete all comments related to this post.
    </&>
</%method>


<%method commentform>
    <%args>
        form
        parent=None
        post
    </%args>
    <%init>
        user = m.comp('/components:user')
    </%init>
<a name="reply"></a>
%   if parent is None:
       <h3>Post a comment for '<% post.headline %>'</h3>
%   else:
       <h3>Reply to '<% parent.subject %>'</h3>
%
% if not actions.CreateComment().access(user, **ARGS):
    Please <&|/components:securehref, href="/login/", action=actions.Login() &>login</&>
    to post a comment !
%   return    
%

    <&|/components:entryform, form=form, action="/blog/comments/post/"&>
        <&/components:field, type="hidden", name="preview", value="0"&>
        <&/components:field, type="hidden", name="post_id"&>
        <&/components:field, type="hidden", name="parent_comment_id"&>
        <&|/components:field, type="text", name="subject", size="50"&>
            Subject
        </&>
        <&|/components:field, type="textarea", name="body", rows="10", cols="50"&>
            Body
        </&>
        <&|/components:row, colspan="2"&>
            <&/components:field, type="submit", value="Post Comment"&>
            <&/components:field, type="button", value="Preview", onclick="document.%s.preview.value=1;document.%s.submit()" % (form.name, form.name)&>
        </&>
    </&>
</%method>

