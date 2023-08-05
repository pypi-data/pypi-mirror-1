<%args>
    comment=None
    post
    form
    preview=None
</%args>

<div class="rightcontrols">
<a href="/blog/<% post.blog.id %>/"><% post.blog.name %></a>
</div>

<& /form:formstatus, form=form &>
<br/>
% if comment is not None:
<&views.myt:view_comment, comment=comment, showpost=True&>
%
% if preview is not None:
<p class="medium">Preview New Comment</p>
<&views.myt:view_comment, comment=preview, showpost=True&>
<hr/>
%
<&forms.myt:commentform, parent=comment, **ARGS&>




