import myghty.component
import myghty.request as request
import highlight
import os
import posixpath as unixpath

"""module components for source code viewing, path translation dhandler.

this package illustrates how to create small template-based components 
within a module component, and also how to write a dhandler as a module 
component."""

class ViewSource(myghty.component.ModuleComponent):
    def do_component_init(self, **params):
        comp = """
            <%global>
                import posixpath as unixpath
            </%global>
            <%args>
                content
                name
                path
                uri
            </%args>

            <%method title>
                <%args scope="subrequest">
                name
                </%args>
                Source of <% name %>
            </%method>
            
            <span class="smallheader">Source of <a href="<% uri %>"><% path %>/</a><% name %></span>
<a href="<% name %>?type=plain">(download)</a>

<pre class="source">
<% content %>
</pre>
        """
        
        dirlist = """
        <%args>
            directories
            files
            name
            binfiles
            parent
            path
        </%args>

            <%method title>
                <%args scope="subrequest">
                name
                </%args>
                Listing of <% name %>
            </%method>

            <div class="smallheader">Source Code Listing of <a href="<% parent %>"><% path %>/</a><% name %>/</div>
            
            <br/>
    <div class="filelist">
    <a href="<% parent %>">(parent directory)</a><br/>
%    for directory in directories:
    <a href="<% directory %>/index"><% directory %>/</a><br/>
%

%    for file in files:
    <a href="<% file %>"><% file %></a><br/>
%

%    for file in binfiles:
    <% file %><br/>
%

    </div>
"""
        self.viewsource = request.instance().interpreter.make_component(comp)
        self.dirlisting = request.instance().interpreter.make_component(dirlist)
        
    def do_run_component(self, m, r, ARGS, **params):
        filename = r.filename

        source_uri = m.interpreter.attributes['source_uri']

        if filename.endswith('/index'):
            (filename, index) = unixpath.split(filename)
        
        fileuri = filename[len(unixpath.commonprefix([m.interpreter.attributes['source_root'], filename])):]

        if os.path.isdir(filename):
            listing = os.listdir(filename)
            files = filter(lambda f: not f.endswith(".pyc") and os.path.isfile(os.path.join(filename, f)), listing)
            binfiles = filter(lambda f: f.endswith(".pyc") and os.path.isfile(os.path.join(filename, f)), listing)
            directories = filter(lambda f: os.path.isdir(os.path.join(filename, f)), listing)
            (path, name) = unixpath.split(fileuri)
            (parent, n2) = unixpath.split(m.get_request_path())
            parent = unixpath.join(parent, '..', 'index')    
            m.subexec(self.dirlisting, directories = directories, files = files, binfiles = binfiles, path=path, name=name, parent = parent)
        else:
            try:
                f = file(filename)
            except IOError:
                m.abort(404)
    
            r.content_type = 'text/html'        
            s = f.read()
   
            if ARGS.get('type', None) == 'plain':
                 r.content_type = 'text/plain'
                 m.write(s)
                 return
 
            s = highlight.highlight(s, filename = fileuri)
    
            (path, name) = unixpath.split(fileuri)
            (uri, n2) = unixpath.split(m.get_request_path())
            uri = unixpath.join(uri, 'index')    
            m.subexec(self.viewsource, content = s, uri = uri, path = path, name=name)


