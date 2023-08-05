from wsgiref.simple_server import *
import myghty.http.WSGIHandler as WSGIHandler

# WSGI server available at:
# http://peak.telecommunity.com/

def handle(environ, start_response):
    return WSGIHandler.handle(environ, start_response,
        data_dir = './cache', 
        path_translate = [(r'/$', '/index.myt')],
        component_root=[
            {'wsgi_common' : './examples/common'},
            {'wsgi_examples' : './'},
            {'wsgi_docs' : './docs'},
        ],
    )

server_address = ('', 8000)
httpd = WSGIServer(server_address, WSGIRequestHandler)
httpd.set_app(handle)
sa = httpd.socket.getsockname()
print "Serving HTTP on", sa[0], "port", sa[1], "..."
httpd.serve_forever()

