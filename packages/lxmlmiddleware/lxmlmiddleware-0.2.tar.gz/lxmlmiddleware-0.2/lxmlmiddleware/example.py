from webob import Response
from lxml import etree
from lxmlmiddleware.middleware import LXMLMiddleware
from paste.httpexceptions import HTTPExceptionHandler

def example_app(environ, start_response):
    return Response('<html><body>Hello, world!</body></html>')(environ, start_response)

class ExampleMiddleware(LXMLMiddleware):
    def manipulate(self, environ, tree):
        tree.append(etree.XML('<div><i>How are you doing?</i></div>'))        
        return tree
    
class ExampleMiddleware2(LXMLMiddleware):
    def manipulate(self, environ, tree):
        tree.append(etree.XML("<div><b>I'm doing find, thank you!</b></div>"))
        return tree

def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""
    return HTTPExceptionHandler(ExampleMiddleware2(ExampleMiddleware(example_app)))
    
