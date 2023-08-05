import zblog.controller
import zblog.database.mappers as mapper
from zblog.domain.user import User
import zblog.util.form as form
import StringIO, os
import zblog.domain.actions as actions
from zblog.controller import access_control

class LoginController(zblog.controller.Controller):
    def form(self):
        f = form.Form('login',[
            form.FormField('username', required=True),
            form.FormField('password', required=True),
        ])
        return f

    @access_control()
    def __call__(self, m, **kwargs):
        f = self.form()
        self.template(m, '/login.myt', form=f)
        
    @access_control(action=actions.Login())
    def login(self, m, r, ARGS, **kwargs):
        f = self.form()
        f.set_request(ARGS)

        u = User.mapper.get_by(name=f['username'].display)
        if u is None or not u.checkpw(f['password'].display):
            u = None
        if u is not None:
            s = m.get_session()
            s['user'] = u
            s.save()

            m.send_redirect("/", hard=True)
        else:
            f.append_error("Login failed")
            self.template(m, '/login.myt', form=f)
    
    @access_control(action=actions.Logout())
    def logout(self, m, **kwargs):
        s = m.get_session()
        if s.has_key('user'):
            del s['user']
            s.save()
            self.template(m, '/login.myt', form=self.form(), status="You have been logged out")
        else:
            self.template(m, '/login.myt', form=self.form(), status="You are not logged in")


    @access_control(login=False, action=actions.Register())
    def register(self, m, ARGS, validate=False):
        form = self.registerform(m)

        form.set_request(ARGS, validate=validate)
        
        if not validate:
            self.template(m, '/register.myt', form=form)
            return
            
        if form['password_set'].value and form['password_set'].value != form['password_repeat'].value:
            form.append_error("Passwords do not match")
            form.isvalid=False
            
        existing = User.mapper.get_by(name=form['name'].value)
        if existing is not None:
            form['name'].append_error("Username '%s' already exists" % form['name'].value)
            form.isvalid=False
            
        if not form.is_valid():
            self.template(m, '/register.myt', form=form)
            return

        mapper.begin()
        user = User()
        form.reflect_to(user)
        user.group=zblog.domain.user.user
        mapper.commit()
        form = self.form()
        form.append_success("Thanks for registering, %s!" % (user.name))
        self.template(m, '/login.myt', form=form)
    
            
    def registerform(self, m):
        f = form.Form('user',[
            form.IntFormField('user_id', attribute='id'),
            form.FormField('name', required=True),
            form.FormField('fullname', required=True),
            form.FormField('password_set', attribute='password', required=True),
            form.FormField('password_repeat', attribute=None, required=True)
        ])
        return f


index = LoginController()

