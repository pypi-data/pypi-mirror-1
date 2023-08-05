<%args>
    blog_user = None
</%args>

% if blog_user:
    <h2>My Blogs</h2>
% else:
    <h2>All Blogs</h2>
%
<&|/data:bloglist, loop=False, user=blog_user&>
% blogs = m.content_args['blogs']
% if len(blogs):
    <ul>
%   for b in blogs:
        <li><a href="<&/data:blogurl, blog=b &>"><% b.name %></a></li>
%        
    </ul>
% elif blog_user:
    You have no blogs ! 
% else:    
    There are no blogs in this system.  Use the 'Manage' function to create blogs.
%
</&>
