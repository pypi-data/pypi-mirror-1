import zblog.controller
import zblog.util.form as formutil
from zblog.domain.user import User
from zblog.domain.blog import Blog
import zblog.database.mappers as mapper
import zblog.domain.actions as actions
from zblog.controller import access_control

class ManageUser(zblog.controller.Controller):
    @access_control(login=True, action=actions.AdminUsers())
    def ajax_edituser(self, m, ARGS, user_id=None, username=None, form=None):
        if form is None:
            form = self.form(m)
        if username is not None:
            user = User.mapper.get_by(name=username)
            if user is not None:
                form.reflect_from(user)
                form['password_set'].required = False
                form['password_repeat'].required = False
            else:
                form.append_error("Username '%s' not found" % username)
        m.comp('/admin/user.myt:userform', form=form)

    @access_control(login=True, action=actions.AdminUsers())
    def edit_user(self, m, ARGS, user_id=None):
        form = self.form(m)

        if user_id:
            form['password_set'].required = False
            form['password_repeat'].required = False
            
        form.set_request(ARGS, validate=True)
        
        if form['password_set'].value and form['password_set'].value != form['password_repeat'].value:
            form.append_error("Passwords do not match")

        if not user_id:
            existing = User.mapper.get_by(name=form['name'].value)
            if existing is not None:
                form['name'].append_error("Username '%s' already exists" % form['name'].value)
            
        if not form.is_valid():
            self.ajax_edituser(m, ARGS, form=form)
            return

        mapper.begin()
        if user_id:
            created = False
            user = User.mapper.get(user_id)
        else:
            created = True
            user = User()

        form.reflect_to(user)
        mapper.commit()
        form.append_success("User '%s' %s" % (user.name, created and 'created' or 'updated'))
        form.reflect_from(user)
        m.comp('/admin/user.myt:userform', form=form)
    
    @access_control(login=True, action=actions.AdminUsers())
    def delete_user(self, m, ARGS, user_id, confirm=False):
        form = self.form(m)
        user = User.mapper.get(user_id)
        if user is None:
            form.append_error("Userid %d not found" % user_id)
            self.ajax_edituser(m, ARGS, form=form)
            return

        if not confirm:
            m.comp('/admin/user.myt:delete_confirm', user=user)
            return
        name = user.name
        mapper.begin()
        mapper.delete(user)
        mapper.commit()
        form.append_success("User '%s' deleted" % name)
        form.clear()
        m.comp('/admin/user.myt:userform', form=form)
            
    def form(self, m):
        f = formutil.Form('user',[
            formutil.IntFormField('user_id', attribute='id'),
            formutil.FormField('name', required=True),
            formutil.FormField('fullname', required=True),
            formutil.FormField('group', required=True, data=[(x,x) for x in zblog.domain.user.groups]),
            formutil.FormField('password_set', attribute='password', required=True),
            formutil.FormField('password_repeat', attribute=None, required=True)
        ])
        return f

index=ManageUser()        