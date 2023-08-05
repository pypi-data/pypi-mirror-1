import zblog
import zblog.controller
import zblog.domain.actions as actions
import re
import myghty.exception as exception

class FrontController(zblog.controller.Controller):
    """initial controller accessed for all pages.
    
    Is used for access control, as well as initial application configuration 
    is loaded via Interpreter attributes.  If configuration file doesnt 
    exist, bounces to "bootstrap" page to create config file.  """

    def check_bootstrap(self, m):
        """checks if we are in "bootstrap mode", which means theres no config   
        or database setup yet."""
        bootstrap = m.resolution.match.group(1).startswith('/bootstrap/')
        if zblog.need_config and not bootstrap:
            m.send_redirect('/bootstrap/', hard=True)
        elif not zblog.need_config and bootstrap:
            m.abort(403)
            
    def __call__(self, m, ARGS):
        """main handling method. does coarse-grained access control check and 
        forwards on to the requested controller."""
        self.check_bootstrap(m)

        if not zblog.need_config:
            # start mapper session.  clears out previous identitymaps and units of
            # work, within the current thread
            zblog.database.mappers.start_session()

        uri = m.resolution.match.group(1)
        try:
            controller = m.fetch_component(uri, resolver_context="frontcontroller", enable_dhandler=True)
        except exception.ComponentNotFound, cfound:
            raise cfound.create_toplevel()
        
        public = getattr(controller.component_source.callable_, 'public', False)
        if not public:
            m.abort(404)
            return
        
        user = self.get_user(m)
        login = getattr(controller.component_source.callable_, 'login', False)
        if login and user is None:
            login = m.fetch_component('/login/', resolver_context="frontcontroller", enable_dhandler=True)
            m.subexec(login)
            return
            
        action = getattr(controller.component_source.callable_, 'action', None)
        if action is not None:
            if not action.access(user, **ARGS):
                m.abort(403)
                return

        m.comp(controller, **m.request_args)
        

        
index = FrontController()

