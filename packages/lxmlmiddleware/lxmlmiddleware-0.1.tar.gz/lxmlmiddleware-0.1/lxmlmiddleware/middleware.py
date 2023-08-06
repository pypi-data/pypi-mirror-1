"""
LXML middleware
"""

import lxml.html
from lxml import etree

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

        # get the response
        response = self.app(environ, start_response)

        # get the DOM, if not already made
        if not isinstance(response, etree._Element):
            try:
                response = etree.fromstring(''.join(response))
            except etree.XMLSyntaxError: # not XML
                environ.pop('lxml.recomposer')
                return response
        
        # manipulate the DOM
        response = self.manipulate(environ, response)

        # recompose the DOM if the last in the chain
        if environ['lxml.recomposer'] is self:
            response = [ lxml.html.tostring(response) ]

        # return the response
        return response

    def manipulate(self, environ, tree):
        """manipulate the DOM; should return an etree._Element"""
        return tree

