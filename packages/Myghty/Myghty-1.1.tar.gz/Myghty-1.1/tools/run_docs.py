"""
tools/run_docs.py documentation runner.  

*** ADVANCED EXAMPLE !!! PUSHES CONFIG TO THE LIMIT ! ***

for a simpler standalone example, please consult /examples/shoppingcart/run_cart.py .

"""

import os, sys, re

# adjust path to use local directory
[sys.path.insert(0, path) for path in ['./lib', './doc/lib', './examples/common', './examples/shoppingcart/lib', './examples/formvisitor/lib']]

# myghty imports
import myghty.http.HTTPServerHandler as HTTPServerHandler
from myghty.resolver import *

# determine port number
try:
    port = int(sys.argv[1])
except:
    port = 8000

# create local cache directory to store generated files + sessions
if not os.access('./cache', os.F_OK):
    os.mkdir('./cache')


# now set up standalone server    
httpd = HTTPServerHandler.HTTPServer(
    port = port,

    # send all request content types through the full resolution chain
    text_only = False,
    
    # handlers.  a list of regular expressions matched to directories to serve
    # or Interpreter configurations.
    handlers = [
        {r'.*/$|.*\.myt$|/source/.*|/examples/shoppingcart/store/.*' : HTTPServerHandler.HSHandler(
            data_dir = './cache',

            #use_static_source = True,
            
            #debug_elements = ['resolution'],

            #disable_unicode=True, 
            resolver_strategy = [
                # caching.  if static_source is turned on, everything below this rule
                # is cached based on the URI as well as contextual modifiers.
                URICache(),

                # create a group that handles all shopping cart URIs
                ConditionalGroup(regexp='/examples/shoppingcart/store/.*', rules = [

                    # create a "request-only" subgroup for resolving the lead module
                    # components.  this isolates request-level resolutions from
                    # subrequest and component resolutions, greatly reducing the
                    # overall number of lookups required per-component.
                    ConditionalGroup(context='request', rules = [
                        #ResolveModule(
                        #         {r'.*/catalog/.*' : 'shoppingcontroller:index.catalog'},
                        #         {r'.*/item/.*' : 'shoppingcontroller:index.item'},
                        #         {r'.*/cart/.*' : 'shoppingcontroller:index.cart'},
                        #         {r'.*/source/.*' : 'shoppingcontroller:index.source'},
                        #     ),
                        ResolvePathModule(
                           'shoppingcontroller',
                           adjust = lambda u: re.sub(r'/examples/shoppingcart/store/', '/', u)
                        ),

                    ]),
    
                    ResolveDhandler(),
                    ResolveUpwards(),
                    ResolveFile(
                        {'store_comp':'./examples/shoppingcart/components'},
                        {'store_templ':'./examples/shoppingcart/templates'},
                        {'store_htdocs':'./examples/shoppingcart/htdocs'},
                       adjust = lambda u: re.sub(r'/examples/shoppingcart/store/', '/', u)
                    ),
                    
                    NotFound()
                ]),
                
                # resolution rules for the /source/ browser
                Conditional(
                    ResolveModule({r'.*' : 'modulecomponents:ViewSource'}),
                    regexp='/source/.*'
                ),
                
                # resolution rules for the documentation viewer
                ConditionalGroup(regexp='^/doc/$|^/doc/.*\.myt$', rules = [
                    PathTranslate(
                        (r'^/doc/$', '/doc/index.myt'),
                    ),
                    
                    # upwards search, i.e. for /autohandler.  the remaining rules
                    # in this chain will be used to match against successive 
                    # /autohandler uris.
                    ResolveUpwards(),
                    
                    AdjustedResolveFile(
                            [(r'^/doc/', r'/')],
                            {'common':'./examples/common'},
                            {'doc_comp':'./doc/components'},
                            {'doc_content':'./doc/content'},
                    ),
                    
                    NotFound()
                ]),

                # default resolution rules, after the above conditionals have not been
                # met
                
                PathTranslate(
                    (r'^/examples', ''),
                    (r'/$', '/index.myt'),
                ),
                
                # if a dhandler is being searched, the remainder of the rules will 
                # be queried with successive /dhandler uris
                ResolveDhandler(),
                ResolveUpwards(),

                ResolveFile(
                    {'common':'./examples/common'},
                    {'example_htdocs':'./examples'},
                ),
            ],
            
            attributes = {
                'store_uri' : '/examples/shoppingcart/store/',
                'store_document_uri' : '/examples/shoppingcart/docs/',
                'store_path' : '/examples/shoppingcart/store/',

                'source_uri' : '/source/',
                'source_root' : './',
                'docs_static_cache': True,
            },
            
        )
        
        },

        # docroots
        {r'/examples/shoppingcart/docs/(.*)' : './examples/shoppingcart/htdocs'},
        {r'/examples/shoppingcart/store/source/(.*)' : './examples/shoppingcart/'},
        {r'/doc/(.*)' : './doc/html'},
        {r'/examples/(.*)' : './examples'},
        {r'/source/(.*)' : '.'},
        {r'/(.*)':'./examples'},


    ]
)
    
print "HTTPServer listening on port %d" % httpd.port


httpd.serve_forever()

