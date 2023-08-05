"""controller package - defines Myghty application controllers"""

__all__ = ['Controller', 'access_control']

from sqlalchemy import *

class Controller(object):
    def template(self, m, template, **kwargs):
        m.subexec(template, **kwargs)
    def get_user(self, m):
        s = m.get_session()
        u = s.get('user', None)
        # import_instance assures that the user deserialized from the session
        # is properly present in the current thread's unit of work context.
        return objectstore.import_instance(u)
        



def access_control(action=None, login=False):
    def decorator(func):
        func.action = action
        func.login = login
        func.public = True
        return func
    return decorator