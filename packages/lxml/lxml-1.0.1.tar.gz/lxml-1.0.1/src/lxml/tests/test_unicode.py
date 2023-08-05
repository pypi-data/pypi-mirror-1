# -*- coding: utf-8 -*-
import unittest, doctest

from common_imports import StringIO, etree, SillyFileLike

ascii_uni = u'a'

uni = u'Ã¡\uF8D2' # klingon etc.

uxml = u"<test><title>test Ã¡\uF8D2</title><h1>page Ã¡\uF8D2 title</h1></test>"

class UnicodeTestCase(unittest.TestCase):
    def test_unicode_xml(self):
        tree = etree.XML(u'<p>%s</p>' % uni)
        self.assertEquals(uni, tree.text)

    def test_unicode_tag(self):
        el = etree.Element(uni)
        self.assertEquals(uni, el.tag)

    def test_unicode_nstag(self):
        tag = u"{%s}%s" % (uni, uni)
        el = etree.Element(tag)
        self.assertEquals(tag, el.tag)

    def test_unicode_qname(self):
        qname = etree.QName(uni, uni)
        tag = u"{%s}%s" % (uni, uni)
        self.assertEquals(qname.text, tag)
        self.assertEquals(unicode(qname), tag)

    def test_unicode_attr(self):
        el = etree.Element('foo', {'bar': uni})
        self.assertEquals(uni, el.attrib['bar'])

    def test_unicode_comment(self):
        el = etree.Comment(uni)
        self.assertEquals(uni, el.text)

    def test_unicode_parse_stringio(self):
        el = etree.parse(StringIO(u'<p>%s</p>' % uni)).getroot()
        self.assertEquals(uni, el.text)

##     def test_parse_fileobject_unicode(self):
##         # parse unicode from unamed file object (not support by ElementTree)
##         f = SillyFileLike(uxml)
##         root = etree.parse(f).getroot()
##         self.assertEquals(unicode(etree.tostring(root, 'UTF-8'), 'UTF-8'),
##                           uxml)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([unittest.makeSuite(UnicodeTestCase)])
    return suite
