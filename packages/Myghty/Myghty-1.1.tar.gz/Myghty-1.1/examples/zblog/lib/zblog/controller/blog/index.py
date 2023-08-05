from zblog.controller import *
import re, string
from zblog.domain.blog import *
import zblog.domain.actions as actions
import zblog.util.form as formutil
import zblog.database.mappers as mapper
from zblog.controller.blog.comments import index as commentcontroller

class BlogHome(Controller):
    @access_control()
    def __call__(self, m, ARGS):
        """shows all the posts within a blog"""
        match = re.search(r'/(\w+)/(?:topic/(\w+)/)?$', m.request_path)
        if match:
            blog_id = match.group(1)
            if blog_id == 'my':
                self.template(m, '/index.myt', blog_user=self.get_user(m))
                return
            keyword = match.group(2) or False
        else:
            m.abort(404)

        blog = Blog.mapper.get(blog_id)
        if blog is None:
            m.abort(404)

        self.template(m, '/blog/index.myt', blog=blog, keyword=keyword)

    @access_control(action=actions.CreatePost())
    def post(self, m, ARGS, blog_id, post_id=None, preview=False):
        """submits a post, or previews it."""
        blog = Blog.mapper.get(blog_id)
        form = self.postform(m, ARGS)
        form.set_request(ARGS, validate=True)
        
        if post_id:
            post = Post.mapper.get(post_id)
            if post is None:
                form.append_error("no post found for id '%s'" % post_id)
                self.template(m, '/blog/index.myt', blog=blog, loadcomponent='/blog/forms.myt:postform', form=form)
                return
        else:
            post = None
            
        if not form.is_valid():
            self.template(m, '/blog/index.myt', blog=blog, loadcomponent='/blog/forms.myt:postform', form=form, post=post)
        elif int(preview):
            if post is None:
                preview = Post()
            else:
                preview = post
            self.reflect_to(m, form, preview, blog)
            self.template(m, '/blog/index.myt', blog=blog, loadcomponent='/blog/forms.myt:postform', form=form, preview=preview, post=post)
        else:
            mapper.begin()
            if post is None:
                post = Post()
            self.reflect_to(m, form, post, blog)
            mapper.commit()
            if not post_id:
                form.append_success("Post added")
            else:
                form.append_success("Post updated")
            self.template(m, '/blog/index.myt', blog=blog, post=post, loadcomponent='/blog/post.myt', viewcomments=False, form=form )

    def reflect_to(self, m, form, post, blog):
        form.reflect_to(post)
        primary = True
        
        post.topics = []
        for keyword in form['topic_keywords'].value.split(' '):
            if not keyword:
                continue
            topic = Topic.mapper.get_by(keyword=keyword)
            if topic is None:
                topic = Topic(keyword=keyword, description=keyword)
            post.topics.append(TopicAssociation(post=post, topic=topic, is_primary=False))
        
        print repr([(t, t.post, t.topic) for t in post.topics.records.keys()])
            
        post.user = self.get_user(m)
        post.blog = blog

    def reflect_from(self, form, post):
        form.reflect_from(post)
        form['topic_keywords'].value = string.join([t.topic.keyword for t in post.topics])

    @access_control(action=actions.CreatePost())
    def new_post(self, m, ARGS, blog_id):
        """provides a blank "submit a post" screen"""
        blog = Blog.mapper.get(blog_id)
        form = self.postform(m, ARGS)
        self.template(m, '/blog/index.myt', loadcomponent='/blog/forms.myt:postform', form=form, blog=blog)
            
    @access_control(action=actions.EditPost())
    def ajax_edit_post(self, m, ARGS, post_id):
        """produces an "edit post" screen, given the id of the post"""
        post = Post.mapper.get(post_id)
        form = self.postform(m, ARGS)
        self.reflect_from(form, post)
        m.comp('/blog/forms.myt:postform', form=form, blog=post.blog, post=post)

    @access_control(action=actions.EditPost())
    def ajax_delete_post(self, m, ARGS, post_id, confirm=False):
        """deletes a post, given its ID."""
        post = Post.mapper.get(post_id)
        blog = post.blog
        if not confirm:
            m.comp('/blog/forms.myt:delete_confirm', post=post)
            return
        form = self.postform(m, ARGS)
        mapper.begin()
        mapper.delete(post)
        mapper.commit()
        form.append_success("Post deleted")
        m.comp('/blog/index.myt:postlist', blog=blog, form=form)

    @access_control()
    def view(self, m, ARGS):
        """views a specific post within a blog as well as its comments"""
        match = re.search(r'/(\w+)/$', m.request_path)
        if match:
            post_id = match.group(1)
        else:
            m.abort(404)
        
        #post = Post.mapper.options(nodefer('body')).get(post_id)
        post = Post.mapper.get(post_id)
        if post is None:
            m.abort(404)

        commentform = commentcontroller.commentform(m, ARGS, post=post)
        self.template(m, '/blog/index.myt', blog=post.blog, post=post, showcomments=True, form=commentform, loadcomponent='/blog/post.myt' )
        
    def postform(self, m, ARGS):
        form=formutil.Form('post', [
            formutil.IntFormField('blog_id'),
            formutil.IntFormField('post_id'),
            formutil.FormField('preview'),
            formutil.FormField('headline', required=True),
            formutil.FormField('topic_keywords'),
            formutil.FormField('summary'),
            formutil.FormField('body', required=True)
        ])
        if ARGS.has_key('post_id'):
            form['post_id'].value = ARGS['post_id']
        if ARGS.has_key('blog_id'):
            form['blog_id'].value = ARGS['blog_id']
        return form
        
index = BlogHome()

