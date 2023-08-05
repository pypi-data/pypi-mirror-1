from zblog.controller import *

class HomePage(Controller):
    @access_control()
    def __call__(self, m, r, ARGS):
        self.template(m, '/index.myt')

index = HomePage()
