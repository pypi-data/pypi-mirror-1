# -*- coding: utf-8 -*-

"""
Test cases related to namespace implementation classes and the
namespace registry mechanism
"""

import unittest

from common_imports import etree, HelperTestCase, doctest

class ETreeNamespaceClassesTestCase(HelperTestCase):
    
    class default_class(etree.ElementBase):
        pass
    class maeh_class(etree.ElementBase):
        def maeh(self):
            return u'maeh'
    class bluff_class(etree.ElementBase):
        def bluff(self):
            return u'bluff'

    def setUp(self):
        super(ETreeNamespaceClassesTestCase, self).setUp()
        parser = etree.XMLParser()
        parser.setElementClassLookup(
            etree.ElementNamespaceClassLookup() )
        etree.setDefaultParser(parser)

    def tearDown(self):
        etree.setDefaultParser()
        super(ETreeNamespaceClassesTestCase, self).tearDown()

    def test_registry(self):
        ns = etree.Namespace(u'ns01')
        ns[u'maeh'] = self.maeh_class

        etree.Namespace(u'ns01').clear()

        etree.Namespace(u'ns02').update({u'maeh'  : self.maeh_class})
        etree.Namespace(u'ns03').update({u'bluff' : self.bluff_class}.items())
        etree.Namespace(u'ns02').clear()
        etree.Namespace(u'ns03').clear()

    def test_ns_classes(self):
        bluff_dict = {u'bluff' : self.bluff_class}
        maeh_dict  = {u'maeh'  : self.maeh_class}

        etree.Namespace(u'ns10').update(bluff_dict)

        tree = self.parse(u'<bluff xmlns="ns10"><ns11:maeh xmlns:ns11="ns11"/></bluff>')

        el = tree.getroot()
        self.assert_(isinstance(el, etree.ElementBase))
        self.assert_(hasattr(el, 'bluff'))
        self.assertFalse(hasattr(el[0], 'maeh'))
        self.assertFalse(hasattr(el[0], 'bluff'))
        self.assertEquals(el.bluff(), u'bluff')
        del el

        etree.Namespace(u'ns11').update(maeh_dict)
        el = tree.getroot()
        self.assert_(hasattr(el, 'bluff'))
        self.assert_(hasattr(el[0], 'maeh'))
        self.assertEquals(el.bluff(), u'bluff')
        self.assertEquals(el[0].maeh(), u'maeh')
        del el

        etree.Namespace(u'ns10').clear()

        tree = self.parse(u'<bluff xmlns="ns10"><ns11:maeh xmlns:ns11="ns11"/></bluff>')
        el = tree.getroot()
        self.assertFalse(hasattr(el, 'bluff'))
        self.assertFalse(hasattr(el, 'maeh'))
        self.assertFalse(hasattr(el[0], 'bluff'))
        self.assert_(hasattr(el[0], 'maeh'))

        etree.Namespace(u'ns11').clear()

    def test_default_tagname(self):
        bluff_dict = {
            None   : self.bluff_class,
            'maeh' : self.maeh_class
            }

        ns = etree.Namespace("uri:nsDefClass")
        ns.update(bluff_dict)

        tree = self.parse(u'''
            <test xmlns="bla" xmlns:ns1="uri:nsDefClass" xmlns:ns2="uri:nsDefClass">
              <ns2:el1/><ns1:el2/><ns1:maeh/><ns2:maeh/><maeh/>
            </test>
            ''')

        el = tree.getroot()
        self.assertFalse(isinstance(el, etree.ElementBase))
        for child in el[:-1]:
            self.assert_(isinstance(child, etree.ElementBase), child.tag)
        self.assertFalse(isinstance(el[-1], etree.ElementBase))

        self.assert_(hasattr(el[0], 'bluff'))
        self.assert_(hasattr(el[1], 'bluff'))
        self.assert_(hasattr(el[2], 'maeh'))
        self.assert_(hasattr(el[3], 'maeh'))
        self.assertFalse(hasattr(el[4], 'maeh'))
        del el

        ns.clear()

    def test_create_element(self):
        bluff_dict = {u'bluff' : self.bluff_class}
        etree.Namespace(u'ns20').update(bluff_dict)

        maeh_dict  = {u'maeh'  : self.maeh_class}
        etree.Namespace(u'ns21').update(maeh_dict)

        el = etree.Element("{ns20}bluff")
        self.assert_(hasattr(el, 'bluff'))

        child = etree.SubElement(el, "{ns21}maeh")
        self.assert_(hasattr(child, 'maeh'))
        child = etree.SubElement(el, "{ns20}bluff")
        self.assert_(hasattr(child, 'bluff'))
        child = etree.SubElement(el, "{ns21}bluff")
        self.assertFalse(hasattr(child, 'bluff'))
        self.assertFalse(hasattr(child, 'maeh'))

        self.assert_(hasattr(el[0], 'maeh'))
        self.assert_(hasattr(el[1], 'bluff'))
        self.assertFalse(hasattr(el[2], 'bluff'))
        self.assertFalse(hasattr(el[2], 'maeh'))

        self.assertEquals(el.bluff(), u'bluff')
        self.assertEquals(el[0].maeh(), u'maeh')
        self.assertEquals(el[1].bluff(), u'bluff')

        etree.Namespace(u'ns20').clear()
        etree.Namespace(u'ns21').clear()

    def test_create_element_default(self):
        bluff_dict = {None : self.bluff_class}
        etree.Namespace(u'ns30').update(bluff_dict)

        maeh_dict  = {u'maeh'  : self.maeh_class}
        etree.Namespace(None).update(maeh_dict)

        el = etree.Element("{ns30}bluff")
        etree.SubElement(el, "maeh")
        self.assert_(hasattr(el, 'bluff'))
        self.assert_(hasattr(el[0], 'maeh'))
        self.assertEquals(el.bluff(), u'bluff')
        self.assertEquals(el[0].maeh(), u'maeh')

        etree.Namespace(None).clear()
        etree.Namespace(u'ns30').clear()

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([unittest.makeSuite(ETreeNamespaceClassesTestCase)])
    optionflags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    suite.addTests(
        [doctest.DocFileSuite('../../../doc/element_classes.txt',
                              optionflags=optionflags)],
        )
    return suite

if __name__ == '__main__':
    unittest.main()
