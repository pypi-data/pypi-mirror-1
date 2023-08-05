import sys
import urllib
import unittest
from paste.fixture import TestApp
from paste.recursive import RecursiveMiddleware

from wsgixml.applyxslt import applyxslt

class TestBasics(unittest.TestCase):
    XML =  """\
<?xml version="1.0"?>
<?xml-stylesheet href="test.xslt" type="application/xml"?>
<doc/>
"""

    XSLT =  """\
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
version="1.0">
<xsl:template match="/">
  <result/>
</xsl:template>
</xsl:stylesheet>
"""

    def setUp(self):
        #
        return

    def app(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'application/xml')])
        if environ['PATH_INFO'].endswith('test.xml'):
            return [self.XML]
        elif environ['PATH_INFO'].endswith('test.xslt'):
            return [self.XSLT]
        return

    def test_1(self):
        app = TestApp(applyxslt(RecursiveMiddleware(self.app)))
        result = app.get('/test.xml')
        result.mustcontain('<result/>')
        result = app.get('/test.xml', headers={'User-Agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.2) Gecko/20060308 Firefox/1.5.0.2'})
        result.mustcontain('<doc/>')
        result = app.get('/test.xml', headers={'User-agent': 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.2) Gecko/20060308 Firefox/1.5.0.2'})
        result.mustcontain('<doc/>')
        result = app.get('/test.xml', headers={'User-Agent': 'Buster ass browser'})
        result.mustcontain('<result/>')
        return


if __name__ == '__main__':
    unittest.main()

