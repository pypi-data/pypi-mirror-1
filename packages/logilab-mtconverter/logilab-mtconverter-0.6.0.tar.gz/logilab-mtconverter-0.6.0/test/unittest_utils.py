# -*- coding: utf-8 -*-
from logilab.common.testlib import TestCase, unittest_main

import locale
from StringIO import StringIO
from logilab.mtconverter import *


class HtmlEscapeTC(TestCase):
        
    def test_escape(self):
        for data, expected in [('toto', 'toto'),
                               ('r&d', 'r&amp;d'),
                               ('23<12 && 3>2', '23&lt;12 &amp;&amp; 3&gt;2'),
                               ('d"h"', 'd&quot;h&quot;'),
                               ("h'", 'h&#39;'),
                               ]:
            self.assertEquals(html_escape(data), expected)

    def test_html_unescape(self):
        for data, expected in [('toto', 'toto'),
                               ('r&amp;d', 'r&d' ),
                               ('23&lt;12 &amp;&amp; 3&gt;2', '23<12 && 3>2'),
                               ('d&quot;h&quot;', 'd"h"'),
                               ('h&#39;', "h'"),
                               ('x &equiv; y', u"x \u2261 y"),
                               ]:
            self.assertEquals(html_unescape(data), expected)


class GuessEncodingTC(TestCase):
        
    def test_emacs_style_declaration(self):
        data = '''# -*- coding: latin1 -*-'''
        self.assertEquals(guess_encoding(data), 'latin1')
        
    def test_emacs_style_declaration_stringIO(self):
        data = '''# -*- coding: latin1 -*-'''
        self.assertEquals(guess_encoding(StringIO(data)), 'latin1')
        
    def test_xml_style_declaration(self):
        data = '''<?xml version="1.0" encoding="latin1"?>
        <root/>'''
        self.assertEquals(guess_encoding(data), 'latin1')
        
    def test_html_style_declaration(self):
        data = '''<html xmlns="http://www.w3.org/1999/xhtml" xmlns:erudi="http://www.logilab.fr/" xml:lang="fr" lang="fr">
<head>
<base href="http://intranet.logilab.fr/jpl/" /><meta http-equiv="content-type" content="text/html; charset=latin1"/>
</head>
<body><p>hello world</p>
</body>
</html>'''
        self.assertEquals(guess_encoding(data), 'latin1')


class GuessMimetymeAndEncodingTC(TestCase):
    def test_base(self):
        format, encoding = guess_mimetype_and_encoding(filename=u"foo.txt", data="xxx")
        self.assertEquals(format, u'text/plain')
        self.assertEquals(encoding, locale.getpreferredencoding())

    def test_set_mime_and_encoding_gz_file(self):
        format, encoding = guess_mimetype_and_encoding(filename=u"foo.txt.gz", data="xxx")
        self.assertEquals(format, u'text/plain')
        self.assertEquals(encoding, u'gzip')
        format, encoding = guess_mimetype_and_encoding(filename=u"foo.txt.gz", data="xxx",
                                                       format='application/gzip')
        self.assertEquals(format, u'text/plain')
        self.assertEquals(encoding, u'gzip')
        format, encoding = guess_mimetype_and_encoding(filename=u"foo.gz", data="xxx")
        self.assertEquals(format, u'application/gzip')
        self.assertEquals(encoding, None)

    def test_set_mime_and_encoding_bz2_file(self):
        format, encoding = guess_mimetype_and_encoding(filename=u"foo.txt.bz2", data="xxx")
        self.assertEquals(format, u'text/plain')
        self.assertEquals(encoding, u'bzip2')
        format, encoding = guess_mimetype_and_encoding(filename=u"foo.txt.bz2", data="xxx",
                                                       format='application/bzip2')
        self.assertEquals(format, u'text/plain')
        self.assertEquals(encoding, u'bzip2')
        format, encoding = guess_mimetype_and_encoding(filename=u"foo.bz2", data="xxx")
        self.assertEquals(format, u'application/bzip2')
        self.assertEquals(encoding, None)

    def test_set_mime_and_encoding_unknwon_ext(self):
        format, encoding = guess_mimetype_and_encoding(filename=u"foo.123", data="xxx")
        self.assertEquals(format, u'application/octet-stream')
        self.assertEquals(encoding, None)

        
class TransformDataTC(TestCase):
    def test_autodetect_encoding_if_necessary(self):
        data = TransformData('''<?xml version="1.0" encoding="latin1"?>
        <root/>''', 'text/xml')
        self.assertEquals(data.encoding, 'latin1')


if __name__ == '__main__':
    unittest_main()
