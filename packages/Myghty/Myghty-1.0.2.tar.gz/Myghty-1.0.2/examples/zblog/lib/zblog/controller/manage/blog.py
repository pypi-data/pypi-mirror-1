import zblog.controller
import zblog.util.form as formutil
from zblog.domain.user import User
from zblog.domain.blog import Blog
import zblog.database.mappers as mapper
import zblog.domain.actions as actions
from zblog.controller import access_control

class ManageBlog(zblog.controller.Controller):        
    @access_control(login=True, action=actions.EditBlog())    
    def ajax_editblog(self, m, ARGS, blog_id=None, form=None):
        if form is None:
            form = self.form(m)
        if blog_id:
            blog = Blog.mapper.get(blog_id)
            form.reflect_from(blog)
        m.comp('/admin/blog.myt:blogedit', form=form)

    @access_control(login=True, action=actions.EditBlog())
    def bloglist(self, m):
        m.comp('/admin/blog.myt:bloglist')
        
    @access_control(login=True, action=actions.EditBlog())
    def edit_blog(self, m, ARGS, blog_id=None):
        form = self.form(m)
        form.set_request(ARGS, validate=True)

        if not form.is_valid():
            self.ajax_editblog(m, ARGS, form=form, blog_id=blog_id)
            return

        owner = User.mapper.get_by(name=form['owner_name'].value)
        if owner is None:
            form.append_error("Could not locate user %s" % form['owner_name'].value)
            self.ajax_editblog(m, ARGS, form=form, blog_id=blog_id)
            return
        
        mapper.begin()

        if blog_id:
            created = False
            blog = Blog.mapper.get(blog_id)
        else:
            created = True
            blog = Blog()

        form.reflect_to(blog)
        blog.owner = owner
        mapper.commit()
        form.append_success("Blog '%s' %s" % (blog.name, created and 'created' or 'updated'))
        form.reflect_from(blog)
        m.comp('/admin/blog.myt:blogedit', form=form)

    @access_control(login=True, action=actions.EditBlog())
    def delete_blog(self, m, ARGS, blog_id=None, confirm=False):
        form= self.form(m)
        blog = Blog.mapper.get(blog_id)
        if blog is None:
            form.append_error("No blog found for id '%s'" % blog_id)
            self.ajax_editblog(m, ARGS, form=form)
            return

        if not confirm:
            m.comp('/admin/blog.myt:delete_confirm', blog=blog)
            return
        
        name = blog.name
        mapper.begin()
        mapper.delete(blog)
        mapper.commit()
        form.append_success("Blog '%s' deleted" % name)
        form.clear()
        m.comp('/admin/blog.myt:blogedit', form=form)

            
    def form(self, m):
        u = self.get_user(m)
        
        f = formutil.Form('blog',[
            formutil.IntFormField('blog_id', attribute='id'),
            formutil.FormField('name', required=True),
            formutil.FormField('description', required=True),
            formutil.FormField('owner_name', required=True, default=u.name, getattribute="owner.name")
        ])
        return f


index = ManageBlog()