"""
Middleware for processing any XML response body to a DOM or Amara binding

Copyright 2006 Uche Ogbuji
Licensed under the Academic Free License version 3.0
"""

from itertools import chain
from util import iterwrapper

class domlette_response_proxy:
    def __init__(blocks):
        from Ft.Xml.Domlette import Parse
        self.root = Parse(''.join(blocks))
        return
    
    def serialize():
        from cStringIO import StringIO
        output = StringIO()
        from Ft.Xml.Domlette import Print
        Print(self.root, stream=output)
        return output.getvalue()


class bindery_response_proxy:
    def __init__(blocks):
        import amara
        self.root = amara.parse(''.join(blocks))
        return
    
    def serialize():
        return self.root.xml()


class deserialize(object):
    """
    Middleware that deserializes any XML response body to a DOM or Amara binding
    """
    def __init__(self, app, response_proxy_class=bindery_response_proxy):
        #Set-up phase
        self.wrapped_app = app
        return

    def __call__(self, environ, start_response):
        #Called for each client request routed through this middleware

        def start_response_wrapper(status, response_headers, exc_info=None):
            #Assume response is not XHTML; do not activate transformation
            environ['wsgixml.deserialize.active'] = False
            #Check for response content type to see whether it is XML
            #That needs to be transformed
            for name, value in response_headers:
                #content-type value is a media type, defined as
                #media-type = type "/" subtype *( ";" parameter )
                media_type = value.split(';')[0]
                if ( name.lower() == 'content-type'
                     and ( media_type.endswith('/xml')
                           or media_type.find('/xml+') != -1 )):
                    environ['applyxslt.active'] = True

            #We ignore the return value from start_response
            start_response(status, response_headers, exc_info)
            #Replace any write() callable with a dummy that gives an error
            #The idea is to refuse support for apps that use write()
            def dummy_write(data):
                raise RuntimeError('deserialize does not support the deprecated write() callable in WSGI clients')
            return dummy_write

        iterable = self.wrapped_app(environ, start_response_wrapper)
        response_blocks = []

        #This function processes each chunk of output (simple string) from
        #the app, returning The modified chunk to be passed on to the server
        def next_response_block(response_iter):
            for block in response_iter:
                if environ['wsgixml.deserialize.active']:
                    response_blocks.append(block)
                    yield '' #Obey buffering rules for WSGI
                else:
                    yield block

        def produce_final_output():
            if environ['wsgixml.deserialize.active']:
                response_proxy = response_proxy_class(response_blocks)
                environ['wsgixml.deserialize.object'] = response_proxy
            yield ''

        return chain(iterwrapper(iterable, next_response_block),
                     produce_final_output())



class serialize(object):
    """
    Serializes response bodies processed by wsgixml.deserialize
    """
    def __init__(self, app):
        #Set-up phase
        self.wrapped_app = app
        return

    def __call__(self, environ, start_response):
        iterable = self.wrapped_app(environ, start_response)
        response_blocks = []

        def produce_final_output():
            if environ['wsgixml.deserialize.active']:
                response_proxy = environ['wsgixml.deserialize.object']
            yield response_proxy.serialize()

        return chain(iterable, produce_final_output())


