from zblog.controller import *
import re
from zblog.domain.blog import *
import zblog.domain.actions as actions
import zblog.util.form as formutil
import zblog.database.mappers as mapper

class Comments(Controller):
    @access_control()
    def __call__(self, m, ARGS):
        """produces a listing of comments for a post"""
        match = re.search(r'/(\w+)/$', m.request_path)
        if match:
            post_id = match.group(1)
        else:
            m.abort(404)

        post = Post.mapper.get(post_id)
        if post is None:
            m.abort(404)

        form = self.commentform(m, ARGS, post)
        self.template(m, '/blog/comments.myt', post=post, form=form)

    @access_control()
    def view(self, m, ARGS):
        """views a specific comment"""
        match = re.search(r'/(\w+)/$', m.request_path)
        if match:
            comment_id = match.group(1)
        else:
            m.abort(404)

        comment = Comment.mapper.get(comment_id)
        if comment is None:
            m.abort(404)

        form = self.commentform(m, ARGS, comment.post, comment)
        self.template(m, '/blog/postcomment.myt', post=comment.post, comment=comment, form=form)
        
    @access_control(action=actions.CreateComment())
    def post(self, m, ARGS, post_id, parent_comment_id, confirm=False, preview=False):
        """posts a comment, or provides a preview display."""
        post = Post.mapper.get(post_id)
        if post is None:
            m.abort(404)

        if parent_comment_id:
            parentcomment = Comment.mapper.get(parent_comment_id)
        else:
            parentcomment = None
        form = self.commentform(m, ARGS, post, comment=parentcomment)
        form.set_request(ARGS, validate=True)
        if not form.is_valid():
            self.template(m, '/blog/postcomment.myt', post=post, form=form, comment=parentcomment)
            return
        if int(preview):
            comment = self.createcomment(m, post, form, parentcomment)
            self.template(m, '/blog/postcomment.myt', post=post, form=form, comment=parentcomment, preview=comment)
            return
        mapper.begin()
        comment = self.createcomment(m, post, form, parentcomment)
        mapper.commit()
        form = self.commentform(m, ARGS, post, comment)
        form.append_success("Comment posted!")
        self.template(m, '/blog/postcomment.myt', post=post, comment=comment, form=form)

    def createcomment(self, m, post, form, parentcomment):
        """creates a new comment from a given form"""
        comment = Comment() 
        comment.id = None
        form.reflect_to(comment)
        comment.user = self.get_user(m)
        comment.post = post
        if parentcomment is not None:
            comment.parent = parentcomment
        return comment
        
    def commentform(self, m, ARGS, post, comment=None):
        """creates a blank comment form"""
        if comment is not None:
            subject = "Re: %s" % comment.subject
        else:
            subject = None

        form=formutil.Form('comment', [
            formutil.IntFormField('post_id'),
            formutil.IntFormField('preview'),
            formutil.IntFormField('parent_comment_id'),
            formutil.FormField('subject', required=True, default=subject),
            formutil.FormField('body', required=True)
        ])
        form['post_id'].value = post.id
        if comment is not None:
            form['parent_comment_id'].value = comment.id
            
        return form
        
index = Comments()    

        
