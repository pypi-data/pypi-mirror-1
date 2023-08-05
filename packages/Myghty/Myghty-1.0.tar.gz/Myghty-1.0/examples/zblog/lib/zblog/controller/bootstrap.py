import zblog.database
import zblog.util.form as form
import StringIO, os
from zblog.controller import *
import zblog.domain.actions as actions

class BootstrapController(Controller):
    """bootstrap controller, is used to receive configuration details 
    and create config.py file. this controller is only used when first 
    configuring the application."""

    @access_control(action=actions.Bootstrap())
    def __call__(self, m, ARGS, dbtype='sqlite'):
        form = self.form(ARGS, post=False)
        self.template(m, '/bootstrap/', form=form, dbtype=dbtype)
    
    @access_control(action=actions.Bootstrap())
    def bootstrap(self, m, ARGS, **kwargs):
        form = self.form(ARGS, post=True)
        if not form.is_valid():
            self.template(m, '/bootstrap/', form=form, **kwargs)
        else:            
            (logstring, error) = self.bootstrap_app(m, form) 
            self.template(m, '/bootstrap/complete.myt', log=logstring, error=error)
    
    @access_control(action=actions.Bootstrap())
    def ajax_dboptions(self, m, ARGS, dbtype):
        m.comp('/bootstrap/index.myt:dboptions', dbtype=dbtype, form=self.form(ARGS))
    
    @access_control(action=actions.Bootstrap())
    def ajax_testconnect(self, m, r, ARGS, dbtype):
        dbform = self.form(ARGS)['dbform']
        dbform.set_request(ARGS)
        kwargs = {}
        for e in dbform:
            kwargs[e.name] = e.value
        try:            
            connect = zblog.database.test_connection(dbtype, kwargs)
            error = None
        except Exception, e:
            error = e
        m.comp('/bootstrap/index.myt:dboptions', dbtype=dbtype, form=self.form(ARGS), connected=(error is None), error=error)
    
    def form(self, ARGS, post=False):
        db_descriptors = zblog.database.dbtypes()
        opt = [(None, '(select)')] + [(desc['name'], desc['description']) for desc in db_descriptors]
        f = form.Form('bootstrap',[
            form.FormField('adminuser', required=True, default='Administrator'),
            form.FormField('adminpw', required=True),
            form.FormField('dbtype', required=True, default='sqlite', data=opt)
        ])

        dbform = form.SubForm('dbform', [])
        f.append(dbform)
        
        dbtype = ARGS.get('dbtype', 'sqlite')
        desc = zblog.database.get_descriptor(dbtype)
        if desc is not None:
            dbform.description = desc['description']
            f['dbtype'].value=dbtype
            for field in desc['arguments']:
                if dbtype == 'sqlite' and field[0] == 'filename':
                    default = './data/zblog.db'
                else:
                    default = field[2]
                dbform.append(form.FormField(field[0], description=field[1], default=default, required=True))

        f.set_request(ARGS, validate=post)
        return f


    def bootstrap_app(self, m, form):
        """when all the arguments are assembled, this method 
        writes out a config file and calls the appropriate 
        modules to create the database schema."""
        s = StringIO.StringIO()
        dbtype = form['dbtype'].value
        desc = zblog.database.get_descriptor(dbtype)
        s.write("""
database = dict(
    driver='%s',
    echo=True,
""" % dbtype)
        subform = form['dbform']
        for arg in desc['arguments']:
            s.write("    %s='%s',\n" % (arg[0], subform[arg[0]].value))
        s.write(""")""")
        
        logger =StringIO.StringIO()
        # write configuration file
        logger.write("Creating configuration file '%s'\n" % m.interpreter.attributes['config_file'])
        f = file(m.interpreter.attributes['config_file'], 'w')
        f.write(s.getvalue())
        f.close()

        try:
            # initialize application config
            zblog.load_config(m.interpreter.attributes['config_file'])

            # create database
            logger.write("Creating application tables\n")
            zblog.database.init_database(admin_username=form['adminuser'].value, admin_password=form['adminpw'].value, logger=logger)
            error = False
        except Exception, e:
            # boom - delete config file
            logger.write("Error occurred: '%s'\ndeleting config file\n" % str(e))
            zblog.reset_config()
            os.remove(m.interpreter.attributes['config_file'])
            error = True

        return (logger.getvalue(), error)

        
index = BootstrapController()
