"""a simple access-control ruleset.  Each class defines a different kind of user "action",
along with a function containing all necessary logic to determine if the action is allowed
for the currently logged in user (if any).  These objects can be used both to disable/hide
links and buttons, as well as when the message comes into a controller to determine whether
to perform the action or produce a 403 Forbidden exception."""
import re, string
import zblog
from zblog.domain.blog import *


actions = {}
class ActionSingleton(type):
    def __call__(self):
        try:
            name = string.lower(re.sub(r"(\w)([A-Z])", r"\1_\2", self.__name__))
            return actions[name]
        except KeyError:
            return actions.setdefault(name, type.__call__(self, name))
    
class Action(object):
    __metaclass__ = ActionSingleton
    def __init__(self, name):
        self.name = name
        
    def access(self, user, **kwargs):
        return False

class Bootstrap(Action):
    """defines the initial config file creation and database creation.  only allowed
    if the application has no configuration defined."""
    def access(self, user, **kwargs):
        return zblog.need_config 
    
class Login(Action):
    def access(self, user, **kwargs):
        return True

class Logout(Action):
    def access(self, user, **kwargs):
        return True

class Manage(Action):
    def access(self, user, **kwargs):
        return user is not None and user.is_administrator()
        
class AdminUsers(Action):
    def access(self, user, **kwargs):
        return user is not None and user.is_administrator()

class LoggedIn(Action):
    def access(self, user, **kwargs):
        return user is not None
                
class EditBlog(Action):
    def access(self, user, blog_id=None, **kwargs):
        if user is None:
            return False
        if blog_id and not user.is_administrator():
            blog = Blog.mapper.get(blog_id)
            if blog is None:
                return False
            return user.id==blog.owner.id
        else:
            return user.is_administrator()

class CreatePost(Action):
    def access(self, user, blog_id=None, blog=None, **kwargs):
        if user is None:
            return False
        if blog is None:
            blog = Blog.mapper.get(blog_id)
            if blog is None:
                return False
        return blog.owner.id==user.id or user.is_administrator()

class EditPost(Action):
    def access(self, user, post_id=None, post=None, **kwargs):
        if user is None:
            return False
        if post is None:
            post = Post.mapper.get(post_id)
            if post is None:
                return False
        return post.user.id==user.id or user.is_administrator() or user.id==post.blog.owner.id

class Register(Action):
    def access(self, user, **kwargs):
        return user is None
    
class CreateComment(Action):
    def access(self, user, **kwargs):
        return user is not None
        
class DeleteComment(Action):
    pass


