from routes.util import redirect_to, url_for

class ApplicationController(object):
    def do_run_component(self, m, r, s, **params):
        m.global_args['url_for'] = url_for
        m.global_args['redirect_to'] = redirect_to