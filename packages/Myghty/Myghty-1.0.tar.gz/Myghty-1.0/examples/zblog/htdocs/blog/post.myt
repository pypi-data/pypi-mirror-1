<%args>
    post
    viewpost=True
    viewcomments=True
</%args>
<%global>
    from zblog.domain.blog import *
</%global>
<%init>
    commentcount = post.comment_count
</%init>


<&views.myt:view_post, post=post&>

% if not viewcomments:
    <a href="/blog/view/<% post.id %>/"><% str(commentcount) %> Comments</a>
% else:
    <a href="#comments"><% str(commentcount) %> Comments</a>
%
<a href="#reply">reply</a>

% if viewcomments:
    <hr/>
    <a name="comments"></a>    
    <& SELF:postcomments, post=post &>    

    <&forms.myt:commentform, **ARGS&>
%

<%method postcomments>
    <%args>
        post
    </%args>
<&|/data:postcomments, loop=False, post=post &>
% comments = m.content_args['comments']
% if len(comments):    
    <& SELF:commentlist, comments=comments &>
% else:    
    No comments !
%
</&>
</%method>


<%method commentlist>
    <%args>
        comments
    </%args>
%   for comment in comments:
    <& views.myt:view_comment, comment=comment &>
    <hr/>    
    <div style="padding-left:20px">
    <&SELF:commentlist, comments=comment.replies&>
    </div>
% 
</%method>