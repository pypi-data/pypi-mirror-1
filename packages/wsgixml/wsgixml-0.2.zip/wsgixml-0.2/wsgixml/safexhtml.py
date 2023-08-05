"""
Middleware that checks for XHTML capability in the client and translates
XHTML to HTML if the client can't handle it

Copyright 2006 Uche Ogbuji
Licensed under the Academic Free License version 3.0
"""

import cStringIO
from itertools import chain
from xml import sax
from Ft.Xml import CreateInputSource
from Ft.Xml.Sax import SaxPrinter
from Ft.Xml.Lib.HtmlPrinter import HtmlPrinter

from util import iterwrapper, get_request_url

XHTML_IMT = "application/xhtml+xml"
HTML_CONTENT_TYPE = 'text/html; charset=UTF-8'


class safexhtml(object):
    """
    Middleware that checks for XHTML capability in the client and translates
    XHTML to HTML if the client can't handle it
    """
    def __init__(self, app):
        #Set-up phase
        self.wrapped_app = app
        return

    def __call__(self, environ, start_response):
        #Handling a client request phase.
        #Called for each client request routed through this middleware

        #Does the client specifically say it supports XHTML?
        #Note saying it accepts */* or application/* will not be enough
        xhtml_ok = XHTML_IMT in environ.get('HTTP_ACCEPT', '')

        #Specialized start_response function for this middleware
        def start_response_wrapper(status, response_headers, exc_info=None):
            #Assume response is not XHTML; do not activate transformation
            environ['safexhtml.active'] = False
            #Check for response content type to see whether it is XHTML
            #That needs to be transformed
            for name, value in response_headers:
                #content-type value is a media type, defined as
                #media-type = type "/" subtype *( ";" parameter )
                if ( name.lower() == 'content-type'
                     and value.split(';')[0] == XHTML_IMT ):
                    #Strip content-length if present (needs to be
                    #recalculated by server)
                    #Also strip content-type, which will be replaced below
                    response_headers = [ (name, value)
                        for name, value in response_headers
                            if ( name.lower()
                                 not in ['content-length', 'content-type'])
                    ]
                    #Put in the updated content type
                    response_headers.append(('content-type', HTML_CONTENT_TYPE))
                    #Response is XHTML, so activate transformation
                    environ['safexhtml.active'] = True
                    break

            #We ignore the return value from start_response
            start_response(status, response_headers, exc_info)
            #Replace any write() callable with a dummy that gives an error
            #The idea is to refuse support for apps that use write()
            def dummy_write(data):
                raise RuntimeError('safexhtml does not support the deprecated write() callable in WSGI clients')
            return dummy_write

        #Get the iterator from the application that will yield response
        #body fragments
        iterable = self.wrapped_app(environ, start_response_wrapper)

        #Gather output strings for concatenation
        #(only used if HTML translation is required)
        response_blocks = []

        #This function processes each chunk of output (simple string) from
        #the app, returning The modified chunk to be passed on to the server
        def next_response_block(response_iter):
            for block in response_iter:
                if xhtml_ok:
                    #The client can handle XHTML, so nothing for this middleware to do
                    #Notice that the original start_response function is passed
                    #On, not this middleware's start_response_wrapper
                    yield block
                else:
                    if environ['safexhtml.active']:
                        response_blocks.append(block)
                        yield '' #Obey buffering rules for WSGI
                    else:
                        yield block

        #After the application has finished sending its response body
        #fragments, if HTML translation is required, it is necessary
        #to send one more chunk, with the fully translated XHTML
        #This is handled by the following function, a generator.
        #If HTML translation is not required the generator produces nothing
        def produce_final_output():
            if not xhtml_ok and environ['safexhtml.active']:
                #Need to convert response from XHTML to HTML 
                xhtmlstr = ''.join(response_blocks) #First concatenate response

                #Now use 4Suite to transform XHTML to HTML
                htmlstr = cStringIO.StringIO()  #Will hold the HTML result
                parser = sax.make_parser(['Ft.Xml.Sax'])
                handler = SaxPrinter(HtmlPrinter(htmlstr, 'UTF-8'))
                parser.setContentHandler(handler)
                #Don't load the XHTML DTDs from the Internet
                parser.setFeature(sax.handler.feature_external_pes, False)
                parser.parse(CreateInputSource(xhtmlstr))
                yield htmlstr.getvalue()

        return chain(iterwrapper(iterable, next_response_block),
                     produce_final_output())

