import sys
import urllib
import unittest
from paste.fixture import TestApp
from paste.recursive import RecursiveMiddleware

from wsgixml.safexhtml import safexhtml

XHTML_IMT = "application/xhtml+xml"
HTML_IMT = "text/html"

class closeablelist:
    def __init__(self, doc):
        self._doc_iter = iter([doc[:20], doc[20:]])

    def __iter__(self):
        return self

    def next(self):
        return self._doc_iter.next()

    def close(self):
        print "ITERATOR CLOSED"


class TestBasics(unittest.TestCase):
    XHTML =  """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" >
  <head>
    <title>Virtual Library</title>
  </head>
  <body>
    <p>Moved to <a href="http://vlib.org/">vlib.org</a>.</p>
  </body>
</html>
"""

    def setUp(self):
        return

    def app(self, environ, start_response):
        #print "using IMT", app.current_imt
        start_response('200 OK', [('Content-Type', self.current_imt)])
        #Swap the IMT used for response (alternate between XHTML_IMT and HTML_IMT)
        return closeablelist(self.XHTML)

    def test_1(self):
        app = TestApp(safexhtml(RecursiveMiddleware(self.app)))

        self.current_imt = HTML_IMT
        result = app.get('/')
        result.mustcontain('XHTML 1')

        self.current_imt = XHTML_IMT
        result = app.get('/')
        self.assert_('<?xml' not in result)

        self.current_imt = HTML_IMT
        result = app.get('/', headers={'Accept': XHTML_IMT})
        result.mustcontain('XHTML 1')

        self.current_imt = XHTML_IMT
        result = app.get('/', headers={'Accept': XHTML_IMT})
        result.mustcontain('XHTML 1')

        self.current_imt = HTML_IMT
        result = app.get('/', headers={'Accept': HTML_IMT})
        result.mustcontain('XHTML 1')

        self.current_imt = XHTML_IMT
        result = app.get('/', headers={'Accept': HTML_IMT})
        self.assert_('<?xml' not in result)

        return


if __name__ == '__main__':
    unittest.main()

