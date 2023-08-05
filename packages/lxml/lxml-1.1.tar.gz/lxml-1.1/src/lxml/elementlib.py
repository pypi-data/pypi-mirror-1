__doc__ = """\
Element class library.

A collection of custom Element classes.
"""

from lxml import etree

class ObjectTreeElement(etree.ElementBase):
    """A simple data-binding like Element class that allows object attribute
    access to its children.

    >>> root = etree.XML("<root xmlns='uri'><a><v>1</v><x>test</x></a></root>")
    >>> root.a.v()
    '1'
    >>> root.a.x()
    'test'
    >>> root.a.v = 2
    >>> root.a.v()
    '2'

    When a non-existing attribute is requested, it is looked up in the
    children under the same namespace as this Element.  Only the first child
    having this tag is considered.  AttributeError is raised if no such child
    is found.

    Setting an attribute results in the value being set as text of the
    respective child element.  Calling an attribute returns the (text) value.
    """
    def __findChild(self, tag):
        for child in self:
            if child.tag == tag:
                return child
        raise AttributeError, "No child found: %s" % tag

    def __getattr__(self, name):
        if name[:1] != '{':
            tag = self.tag
            if tag[0] == '{':
                name  = tag[:tag.index('}')+1] + name
        return self.__findChild(name)

    def __setattr__(self, name, value):
        if name[:1] != '{':
            tag = self.tag
            if tag[0] == '{':
                name  = tag[:tag.index('}')+1] + name
        element = self.__findChild(name)
        if value is not None:
            self.__value_type = type(value)
            if not isinstance(value, basestring):
                value = str(value)
        else:
            del self.__value_type
        element.text = value

    def __call__(self):
        try:
            return self.__value_type(self.text)
        except AttributeError:
            return self.text
