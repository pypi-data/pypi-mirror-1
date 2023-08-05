"""
WSGI middleware that applies XSLT to an XML response body if needed

Copyright 2006 Uche Ogbuji
Licensed under the Academic Free License version 3.0
"""

import re
from cStringIO import StringIO
from itertools import chain
from xml import sax
from Ft.Xml import Sax, InputSource, CreateInputSource
from Ft.Xml.Xslt import Processor
#from Ft.Lib.Uri import OsPathToUri

from util import iterwrapper, get_request_url

USER_AGENT_REGEXEN = [
'.*MSIE 5.5.*',
'.*MSIE 6.0.*',
'.*MSIE 7.0.*',
'.*Gecko/2005.*',
'.*Gecko/2006.*',
'.*Opera/9.*',
'.*AppleWebKit/31.*',
'.*AppleWebKit/4.*',
]

USER_AGENT_REGEXEN = [ re.compile(regex) for regex in USER_AGENT_REGEXEN ]


class find_xslt_pi(sax.ContentHandler):
    def __init__(self, parser):
        parser.setContentHandler(self)
        self.parser = parser
        return

    def startDocument(self):
        self.ecount = 0
        self.xslt_pi = None

    def startElementNS(self, name, qname, attribs):
        self.ecount += 1
        if self.ecount == 2:
            #We're now within the doc proper, so we're done
            self.parser.setProperty(Sax.PROPERTY_YIELD_RESULT, self.xslt_pi)
        return
            
    def processingInstruction(self, target, data):
        if target == u'xml-stylesheet':
            data = data.split()
            pseudo_attrs = {}
            for d in data:
                seg = d.split('=')
                if len(seg) == 2:
                    pseudo_attrs[seg[0]] = seg[1][1:-1]

            # PI must have both href, type pseudo-attributes;
            # type pseudo-attr must match valid XSLT types;
            # media pseudo-attr must match preferred media
            # (which can be None)
            if (pseudo_attrs.has_key('href')
                and pseudo_attrs.has_key('type')
                and pseudo_attrs['type'] in Processor.XSLT_IMT):
                    self.xslt_pi = pseudo_attrs['href']
                    self.parser.setProperty(Sax.PROPERTY_YIELD_RESULT, self.xslt_pi)
        return


class applyxslt(object):
    """
    Middleware that checks for XSLT transform capability in the client and
    performs the transform on the server side if one is required, and the
    client can't do it
    """
    def __init__(self, app):
        #Set-up phase
        self.wrapped_app = app
        return

    def __call__(self, environ, start_response):
        #Guess whether the client supports XML+XSLT?
        #See: http://copia.ogbuji.net/blog/2006-08-26/LazyWeb_Ho
        client_ua = environ.get('HTTP_USER_AGENT', '')
        xslt_ok = True in [ ua_pat.match(client_ua) is not None
                            for ua_pat in USER_AGENT_REGEXEN ]

        #We'll hack a bit for dealing with Python's imperfect nested scopes.
        response_params = []
        def start_response_wrapper(status, response_headers, exc_info=None):
            #Assume response does not use XSLT; do not activate middleware
            environ['applyxslt.active'] = False
            #Check for response content type to see whether it is XML
            for name, value in response_headers:
                #content-type value is a media type, defined as
                #media-type = type "/" subtype *( ";" parameter )
                media_type = value.split(';')[0]
                if ( name.lower() == 'content-type'
                     and ( media_type.endswith('/xml')
                           or media_type.find('/xml+') != -1 )):
                    environ['applyxslt.active'] = True
            response_params.extend([status, response_headers, exc_info])
            #Replace any write() callable with a dummy that gives an error
            #The idea is to refuse support for apps that use write()
            def dummy_write(data):
                raise RuntimeError('applyxslt does not support the deprecated write() callable in WSGI apps')
            return dummy_write

        #Get the iterator from the application that will yield response
        #body fragments
        iterable = self.wrapped_app(environ, start_response_wrapper)
        (status, response_headers, exc_info) = response_params

        #This function processes each chunk of output (simple string) from
        #the app, returning The modified chunk to be passed on to the server
        def next_response_block(response_iter):
            if xslt_ok or not environ['applyxslt.active']:
                #The client can handle XSLT, or it's not an XML source doc,
                #so nothing for this middleware to do
                start_response(status, response_headers, exc_info)
                for block in response_iter.next():
                    yield block
            else:
                yield produce_final_output(''.join(response_iter))
                return  

        #After the app has finished sending its response body fragments
        #if transform is required, it's necessary to send one more chunk,
        #with the fully transformed result
        def produce_final_output(response, response_headers=response_headers):
            if not xslt_ok and environ['applyxslt.active']:
                #Now check for a Stylesheet PI
                parser = Sax.CreateParser()
                parser.setFeature(Sax.FEATURE_GENERATOR, True)
                handler = find_xslt_pi(parser)
                pi_iter = parser.parse(CreateInputSource(response))
                try:
                    xslt_pi = pi_iter.next()
                except StopIteration:
                    xslt_pi = None
                if xslt_pi:
                    result = StringIO()
                    processor = Processor.Processor()
                    #srcAsUri = OsPathToUri()
                    source = InputSource.DefaultFactory.fromString(
                        response, get_request_url(environ))
                    if environ.has_key('paste.recursive.include'):
                        #paste's recursive facilities are available, to
                        #so we can get the XSLT with a middleware call
                        #rather than a full Web invocation
                        xslt_resp = environ['paste.recursive.include'](xslt_pi)
                        #FIXME: this should be relative to the XSLT, not XML
                        isrc = InputSource.DefaultFactory.fromString(
                            xslt_resp.body, get_request_url(environ))
                        processor.appendStylesheet(isrc)
                        processor.run(source, outputStream=result,
                                      ignorePis=True)
                    else:
                        #We have to make a full Web call to get the XSLT.
                        #4Suite will do that for us in processing the PI
                        processor.run(source, outputStream=result)

                    #Strip content-length if present (needs to be
                    #recalculated by server)
                    #Also strip content-type, which will be replaced below
                    response_headers = [ (name, value)
                        for name, value in response_headers
                            if ( name.lower()
                                 not in ['content-length', 'content-type'])
                    ]
                    #Put in the updated content type
                    imt = processor.outputParams.mediaType
                    response_headers.append(('content-type', imt))
                    start_response(status, response_headers, exc_info)
                    return result.getvalue()
                    
            #If it reaches this point, no XSLT was applied.
            return

        return iterwrapper(iterable, next_response_block)


#if __name__ == '__main__':
    
