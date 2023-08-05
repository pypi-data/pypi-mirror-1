
<%method ajax>
<%init>
    return m.comp('/ajax/myghtyjax.myt:init', 
        editblog = {
            'handler_uri':'/manage/blog/ajax_editblog/', 
            'exectype':'writedom', 
            'dom_id':'opwindow'
        },
        bloglist = {
            'handler_uri':'/manage/blog/bloglist/',
            'exectype':'writedom',
            'dom_id':'opwindow'
        },
        action_editblog = {
            'handler_uri':'/manage/blog/edit_blog/', 
            'exectype':'writedom', 
            'dom_id':'opwindow'
        },
        action_deleteblog = {
            'handler_uri':'/manage/blog/delete_blog/', 
            'exectype':'writedom', 
            'dom_id':'opwindow'
        },
        )
</%init>
</%method>

<%method links>
% for link in [('javascript:editblog()', 'Create Blog'), ('javascript:bloglist()', 'Edit Blog')]:
<% m.content(url=link[0], text=link[1]) %>
%
</%method>

<%method blogedit>
    <%args>
        form
    </%args>

<& /form:formstatus, form=form &>
<&|/components:entryform, ajaxtarget="action_editblog", form=form, columns=2&>
    <&/components:field, type="hidden", name='blog_id'&>
    <&|/components:field, type="text", name='name'&>
        Blog Name
    </&>
    <&|/components:field, type="text", name='description'&>
        Description
    </&>
    <&|/components:field, type="text", name='owner_name'&>
        Owner
    </&>
    <&|/components:row, colspan="2"&>
% if form['blog_id'].display:
    <&/components:field, type="submit", value="Update Blog"&>
    <&/components:field, type="button", value="Delete Blog", onclick=m.comp('/components:ajaxaction', target="action_deleteblog", form=form)&>
% else:  
    <&/components:field, type="submit", value="Create Blog" &>
%
    </&>
</&>    
</%method>

<%method bloglist>

<&|/components:entryform, name="lookupform", onsubmit="editblog({'blog_id':document.lookupform.blog.value});return false", columns=2&>
<tr>
    <td>Select a blog:</td>
    <td>
    <&/components:dropdown, name="blog", data=[(blog.id, blog.name) for blog in m.comp('/data:bloglist')] &>
    <&/components:submit, value="Go"&>
    </td>
</tr>
</&>
</%method>

<%method delete_confirm>
    <%args>
        blog
    </%args>
    <&|/components:confirm, yes="action_deleteblog({'blog_id':'%s','confirm':1})" % blog.id, 
                no="editblog({'blog_id':'%s'})" % blog.id&>
    Are you sure you want to delete blog '<% blog.name %>'?
    This will delete all posts and comments within this blog.
    </&>
</%method>