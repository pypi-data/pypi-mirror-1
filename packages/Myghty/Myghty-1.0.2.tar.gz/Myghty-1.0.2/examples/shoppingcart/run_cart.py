"""shopping cart runner."""

import os, sys, re

[sys.path.insert(0, path) for path in ['../../lib', '../../doc/lib', './lib']]

import myghty.http.HTTPServerHandler as HTTPServerHandler

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

    # port num
    port = port,

    handlers = [
    
        # serve all URIs that do not start with /docs/ with an HTTPHandler.
        {r'(?!/docs/)' : HTTPServerHandler.HSHandler(
            data_dir = './cache',

            # resolve URIs in the 'shoppingcontroller' module first.
            # here, we do it directly by path.  But it can also be
            # broken down into regular expressions for each component
            # via the 'module_components' parameter.
            module_root = ['shoppingcontroller'],

            # else, resolve URIs to one of three component roots.
            component_root = [            
                        {'store_comp':'./components'},
                        {'store_templ':'./templates'},
                        {'store_htdocs':'./htdocs'},
                    ],

            # interpreter attributes, custom config settings used by the 
            # shopping cart controller.
            attributes = {
                'store_uri' : '/',
                'store_document_uri' : '/docs/',
                'store_path' : '/',
            },
            
            )
        
        },

        # docroots, used to determine r.filename, and 
        # also will be served directly if Interpreter rules did not match.
        {r'/source/(.*)' : './'},
        {r'/docs/(.*)' : './htdocs'},
    ]
)
    
print "HTTPServer listening on port %d" % httpd.port

httpd.serve_forever()

