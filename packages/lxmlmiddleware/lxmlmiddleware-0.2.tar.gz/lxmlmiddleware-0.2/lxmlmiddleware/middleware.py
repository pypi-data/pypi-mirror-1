"""
LXML middleware
"""

import lxml.html
from lxml import etree
from webob import Request, Response

class LXMLMiddleware(object):
    """
    abstract base class; inherit from and implement the manipulate method
    """

    def __init__(self, app):
        self.app = app

    ### methods dealing with HTTP
    def __call__(self, environ, start_response):

        # set up to recompose on the way out
        if not 'lxml.recomposer' in environ:
            environ['lxml.recomposer'] = self

        request = Request(environ)
        # get the response
        response = request.get_response(self.app)
        response.decode_content()

        # get the DOM, if not already made
        # TODO: check response.content_type
        if not 'lxml.etree' in environ:
            try:
                environ['lxml.etree'] = etree.fromstring(response.body)
            except etree.XMLSyntaxError: # not XML
                environ.pop('lxml.recomposer')
                return response(environ, start_response)
        
        # manipulate the DOM
        environ['lxml.etree'] = self.manipulate(environ, environ['lxml.etree'])

        # recompose the DOM if the last in the chain
        if environ['lxml.recomposer'] is self:
            response.body = lxml.html.tostring(environ['lxml.etree'])

        # return the response
        return response(environ, start_response)        


    def manipulate(self, environ, tree):
        """manipulate the DOM; should return an etree._Element"""
        return tree

