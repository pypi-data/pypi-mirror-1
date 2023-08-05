import zblog.controller
import zblog.util.form as formutil
import zblog.database.mappers as mapper
import zblog.domain.actions as actions
import zblog.controller.manage.blog as manageblog

from zblog.controller import access_control

class Manage(zblog.controller.Controller):

    @access_control(login=True)    
    def __call__(self, m, r, ARGS):
        self.template(m, '/admin/index.myt')


index = Manage()
