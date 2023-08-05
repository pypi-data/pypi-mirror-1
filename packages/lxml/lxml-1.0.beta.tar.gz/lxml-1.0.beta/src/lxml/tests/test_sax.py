# -*- coding: utf-8 -*-

"""
Test cases related to SAX I/O
"""

import unittest, doctest
from StringIO import StringIO

from common_imports import HelperTestCase
from lxml import sax

class ETreeSaxTestCase(HelperTestCase):

    def test_etree_sax_simple(self):
        tree = self.parse('<a>ab<b/>ba</a>')
        xml_out = self._saxify_serialize(tree)
        self.assertEquals('<a>ab<b/>ba</a>',
                          xml_out)

    def test_etree_sax_double(self):
        tree = self.parse('<a>ab<b>bb</b>ba</a>')
        xml_out = self._saxify_serialize(tree)
        self.assertEquals('<a>ab<b>bb</b>ba</a>',
                          xml_out)

    def test_etree_sax_attributes(self):
        tree = self.parse('<a aa="5">ab<b b="5"/>ba</a>')
        xml_out = self._saxify_serialize(tree)
        self.assertEquals('<a aa="5">ab<b b="5"/>ba</a>',
                          xml_out)

    def test_etree_sax_ns1(self):
        tree = self.parse('<a xmlns="bla">ab<b>bb</b>ba</a>')
        new_tree = self._saxify_unsaxify(tree)
        root = new_tree.getroot()
        self.assertEqual(root.tag,
                         '{bla}a')
        self.assertEqual(root[0].tag,
                         '{bla}b')

    def test_etree_sax_ns2(self):
        tree = self.parse('<a xmlns="blaA">ab<b:b xmlns:b="blaB">bb</b:b>ba</a>')
        new_tree = self._saxify_unsaxify(tree)
        root = new_tree.getroot()
        self.assertEqual(root.tag,
                         '{blaA}a')
        self.assertEqual(root[0].tag,
                         '{blaB}b')

    def test_element_sax(self):
        tree = self.parse('<a><b/></a>')
        a = tree.getroot()
        b = a[0]

        xml_out = self._saxify_serialize(a)
        self.assertEquals('<a><b/></a>',
                          xml_out)

        xml_out = self._saxify_serialize(b)
        self.assertEquals('<b/>',
                          xml_out)

    def test_element_sax_ns(self):
        tree = self.parse('<a:a xmlns:a="blaA"><b/></a:a>')
        a = tree.getroot()
        b = a[0]

        new_tree = self._saxify_unsaxify(a)
        root = new_tree.getroot()
        self.assertEqual(root.tag,
                         '{blaA}a')
        self.assertEqual(root[0].tag,
                         'b')

        new_tree = self._saxify_unsaxify(b)
        root = new_tree.getroot()
        self.assertEqual(root.tag,
                         'b')
        self.assertEqual(len(root),
                         0)

    def test_etree_sax_handler_default_ns(self):
        handler = sax.ElementTreeContentHandler()
        handler.startDocument()
        handler.startPrefixMapping(None, 'blaA')
        handler.startElementNS(('blaA', 'a'), 'a', {})
        handler.startPrefixMapping(None, 'blaB')
        handler.startElementNS(('blaB', 'b'), 'b', {})
        handler.endElementNS(  ('blaB', 'b'), 'b')
        handler.endPrefixMapping(None)
        handler.startElementNS(('blaA', 'c'), 'c', {})
        handler.endElementNS(  ('blaA', 'c'), 'c')
        handler.endElementNS(  ('blaA', 'a'), 'a')
        handler.endPrefixMapping(None)
        handler.endDocument()

        new_tree = handler.etree
        root = new_tree.getroot()
        self.assertEqual(root.tag,
                         '{blaA}a')
        self.assertEqual(root[0].tag,
                         '{blaB}b')
        self.assertEqual(root[1].tag,
                         '{blaA}c')

    def test_etree_sax_redefine_ns(self):
        handler = sax.ElementTreeContentHandler()
        handler.startDocument()
        handler.startPrefixMapping('ns', 'blaA')
        handler.startElementNS(('blaA', 'a'), 'ns:a', {})
        handler.startPrefixMapping('ns', 'blaB')
        handler.startElementNS(('blaB', 'b'), 'ns:b', {})
        handler.endElementNS(  ('blaB', 'b'), 'ns:b')
        handler.endPrefixMapping('ns')
        handler.startElementNS(('blaA', 'c'), 'ns:c', {})
        handler.endElementNS(  ('blaA', 'c'), 'ns:c')
        handler.endElementNS(  ('blaA', 'a'), 'ns:a')
        handler.endPrefixMapping('ns')
        handler.endDocument()

        new_tree = handler.etree
        root = new_tree.getroot()
        self.assertEqual(root.tag,
                         '{blaA}a')
        self.assertEqual(root[0].tag,
                         '{blaB}b')
        self.assertEqual(root[1].tag,
                         '{blaA}c')

    def test_etree_sax_no_ns(self):
        handler = sax.ElementTreeContentHandler()
        handler.startDocument()
        handler.startElement('a', {})
        handler.startElement('b', {})
        handler.endElement('b')
        handler.startElement('c') # with empty attributes
        handler.endElement('c')
        handler.endElement('a')
        handler.endDocument()

        new_tree = handler.etree
        root = new_tree.getroot()
        self.assertEqual(root.tag,    'a')
        self.assertEqual(root[0].tag, 'b')
        self.assertEqual(root[1].tag, 'c')

    def test_etree_sax_error(self):
        handler = sax.ElementTreeContentHandler()
        handler.startDocument()
        handler.startElement('a')
        self.assertRaises(sax.SaxError, handler.endElement, 'b')

    def test_etree_sax_error2(self):
        handler = sax.ElementTreeContentHandler()
        handler.startDocument()
        handler.startElement('a')
        handler.startElement('b')
        self.assertRaises(sax.SaxError, handler.endElement, 'a')

    def _saxify_unsaxify(self, saxifiable):
        handler = sax.ElementTreeContentHandler()
        sax.ElementTreeProducer(saxifiable, handler).saxify()
        return handler.etree
        
    def _saxify_serialize(self, tree):
        new_tree = self._saxify_unsaxify(tree)
        f = StringIO()
        new_tree.write(f)
        return f.getvalue()

    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([unittest.makeSuite(ETreeSaxTestCase)])
    suite.addTests(
        [doctest.DocFileSuite('../../../doc/sax.txt')])
    return suite

if __name__ == '__main__':
    unittest.main()
