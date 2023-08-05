from public cimport _Element, ElementBase, elementFactory, import_etree

from lxml import etree
import_etree(etree)

cdef class MyElement(ElementBase):
    pass

etree.setDefaultElementClass(MyElement)

cdef _Element el
el = etree.Element("test")
print type(el), el is elementFactory(el._doc, el._c_node)
