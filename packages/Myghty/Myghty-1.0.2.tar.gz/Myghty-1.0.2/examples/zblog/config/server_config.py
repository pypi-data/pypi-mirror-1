
"""Myghty server configuration.  should be neutral to HTTP environment, i.e. WSGI, standalone, etc.

This file should be executed in a context that includes "root" as the path to the application root."""


data_dir=os.path.join(root, 'cache')

resolver_strategy = [
    # request-level resolution: everything goes to the front controller
    ConditionalGroup(
            context="request", rules=[
                ResolveModule({r'(.*)' : 'zblog.controller.front:index'}),
                NotFound(),
            ]
    ),
    
    # front-controller resolution: front controller forwards requests into this realm
    # after performing security checks
    ConditionalGroup(
        context="frontcontroller", rules=[
            ResolvePathModule(os.path.join(root, 'lib/zblog/controller'), path_stringtokens=['index'], path_moduletokens=['index']),
            NotFound()
        ]
    ),
    
    # component/template resolution, for subrequests, component calls, inheritance
    
    # autohandlers
    ResolveUpwards(),
    
    # for the 'components' directory, we append '.myc' to incoming filenames so templates dont have to 
    # specify
    ResolveFile({'components':os.path.join(root, 'components')}, adjust=lambda u: re.sub(r'$', '.myc', u)),
    
    # page-level resolution; we convert directory names to index.myt
    PathTranslate((r'/$', '/index.myt')),
    ResolveFile({'htdocs':os.path.join(root, 'htdocs')}),
]

#debug_elements=['resolution']

attributes = {
    'config_file' : os.path.join(root, 'config/config.py'),
}

def preproc(source):
    """source pre-processor.  adds an import to the top of all components."""
    return """
<%global>
import zblog.domain.actions as actions    
</%global>
""" + source
python_pre_processor = preproc



# startup stuff.
import zblog
import zblog.database
zblog.load_config(attributes['config_file'])

