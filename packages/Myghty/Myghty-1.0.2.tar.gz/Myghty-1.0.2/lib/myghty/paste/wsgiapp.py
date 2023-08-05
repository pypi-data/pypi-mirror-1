import sys, os

from paste.util import import_string
import myghty.http.WSGIHandler as WSGIHandler
from myghty.resolver import *

from myghty.ext.routeresolver import RoutesResolver

def make_myghty_app(global_conf, 
                    package_name=None,
                    root_path=None,
                    **app_conf):
    if package_name:
        package = package_name
        if isinstance(package, (str, unicode)):
            package = import_string.simple_import(package+'.webconfig')
    
    config = package.config

    def myghtyapp(environ, start_response):
        return WSGIHandler.handle(environ, start_response,
                                  **config
                                  )
    return myghtyapp
    