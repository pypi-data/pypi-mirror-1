import re
from cStringIO import StringIO
import unittest

from domstripper import DOMStripper

class TestDOMStripper(unittest.TestCase):
    def setUp(self):
        pass
    
    def _trim_whitespace(self, html):
        return re.sub('>\s+<','><', html).strip()
    
    def test_stripper(self):
        
        doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">\n'
        html = doctype + '''<html><head><title>Title</title><meta content="incomplete"></head>
        <body valign="top"><div id="main">Some stuff</div>
          <div id="junk">We dont want to keep this.</div>
        <blockquote>Blockquote 1</blockquote>
        <blockquote>Blockquote 2</blockquote>
        <a href="junk">More junk</a>
        </body></html>'''
        
        file = StringIO(html)
        stripper = DOMStripper(file, ['#main','blockquote'])
        html = stripper.getvalue()
        html = self._trim_whitespace(html)
        
        expect = doctype + '''<html>
        <head>
        <title>Title</title>
        <meta content="incomplete"/>
        </head>
        <body valign="top">
          <div id="main">Some stuff</div>
          <blockquote>Blockquote 1</blockquote>
          <blockquote>Blockquote 2</blockquote>
          
        </body>
        </html>'''
        expect = self._trim_whitespace(expect)
        
        #if html != expect:
        #    print "GOT"
        #    print html
        #    print "EXPECTED"
        #    print expect
        self.assertEqual(html, expect)
        
    def test_keep_just_links(self):
        doctype = '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">\n'
        html = doctype + '''<html><head><title>Title</title></head><body>
        <p><a href="google">Google</a></p>
        <div><a href="yahoo">Yahoo</a></div>
        <a href="strong"><strong>included</strong></a>
        </body></html>'''
        
        file = StringIO(html)
        stripper = DOMStripper(file, ['a'])
        html = stripper.getvalue()
        html = self._trim_whitespace(html)
        
        expect = doctype + '''<html><head><title>Title</title></head><body>
        <a href="google">Google</a>
        <a href="yahoo">Yahoo</a>
        <a href="strong"><strong>included</strong></a>
        </body></html>'''
        expect = self._trim_whitespace(expect)
        
        if html != expect:
            print "GOT"
            print html
            print "EXPECTED"
            print expect
        self.assertEqual(html, expect)        
        
    
if __name__ == '__main__':
    unittest.main()
        