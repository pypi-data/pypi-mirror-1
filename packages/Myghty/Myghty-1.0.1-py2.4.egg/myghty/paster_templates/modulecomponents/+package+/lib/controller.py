class SimpleController(object):
    """a Myghty controller that delivers a welcome page and a login system."""

    def do_component_init(self, *args, **kwargs):
        pass

    def __call__(self, m, **kwargs):
        """the default callable on this SimpleController.  useful with 
        module-path resolution to produce a result when no further path tokens exist."""
        if m.request_path != '/':
            m.abort(404)
        self.welcome_page(m, **kwargs)        
        
    def welcome_page(self, m, **kwargs):
        m.subexec("index.myt")

    def login(self, m, s, username=None, password=None, cmd=None, **kwargs):
        """displays a login page and processes login information.  note 
        the presence of the 's' argument which represents the session.  the 's'
        variable is configured in the webconfig.py file via 'use_session=True'."""
        if username is not None:
            user = _validate_user(username, password)
            if user is not None:
                s['user'] = user
                s.save()
                self.welcome_page(m, **kwargs)
            else:
                m.subexec("login.myt", username=username, failed=True)
        elif cmd == 'logout':
            del s['user']
            s.save()
            m.subexec("logout.myt")
        else:
            m.subexec("login.myt")
        
# establish an instance of SimpleController as 'index'
index = SimpleController()


# private objects and methods, which are preceded by an underscore
# to mark as private when using the ResolvePathModule resolver

class _User(object):
    """represents a logged-in user."""
    def __init__(self, username, fullname):
        self.username = username
        self.fullname = fullname            


def _validate_user(username, password):
    """given a username and password, returns a valid User object
    or None if no user could be found.  """

    # some stub code.  
    if username == 'testuser' and password == 'password':
        return _User('testuser', 'Test User')
    else:
        return None
