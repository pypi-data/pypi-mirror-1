import os, sys
from myghty.resolver import *

publish_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.extend((publish_dir + '/lib',) )

# The following options are passed directly into Myghty, so all configuration options
# available to the Myghty handler are available for your use here
config = {}


config['data_dir'] = os.path.join(publish_dir, 'cache')

config['component_root'] = [
    {'templates' : os.path.join(publish_dir, 'templates')},
    {'comp' : os.path.join(publish_dir, 'components')},
]


config['use_session'] = True
config['resolver_strategy'] = [

              # request-level resolution
              ConditionalGroup(context='request', rules=[

                      # bounce anything that is not "/" or ".myt" down to silent "not found"
                      # controller, which will forward out of Myghty to the Paste file handler
                      ConditionalGroup(regexp=r'(?!.*(/|\.myt)$)', rules = [
                              NotFound(silent=True)
                      ]),

                      # everything else request-level is handled by the controller.
                      # here we are using ResolvePathModule to automatically match pathnames
                      # to methods on objects inside the controller.  Other options include
                      # the more explicit ResolveModule as well as the new Routes resolver.
                      ResolvePathModule('controller'),

                      # ...or not found.
                      NotFound(),
              ]),

              # these rules then handle all other component calls,
              # including subrequest, component, and inherited
              PathTranslate(),
              ResolveDhandler(),
              URICache(),
              ResolveUpwards(),
              ResolvePathModule(),
              ResolveModule(),
              ResolveFile()
          ]
