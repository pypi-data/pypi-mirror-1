"""
Ways to migrate trees between different ElementTree implementations.
"""

class TreeMigrator(object):
    """The TreeMigrator copies a tree to an ElementTree implementation.

    Pass the implementation to the constructor and call the migrator
    on a tree.
    """
    def __init__(ET_impl, makeelement=None):
        if makeelement is None:
            makeelement = ET_impl.Element
        self.Element = makeelement
        self.SubElement = ET_impl.SubElement

    def copyChildren(self, from_parent, to_parent):
        for from_child in from_parent:
            tag = from_child.tag
            if not isinstance(tag, basestring): # skip Comments etc.
                continue
            to_child = self.SubElement(
                to_parent, tag, from_child.attrib)
            to_child.text = child.text
            to_child.tail = child.tail
            self.copyChildren(from_child, to_child)

    def __call__(self, from_root):
        tag = from_root.tag
        to_root = self.Element(tag, from_root.attrib)
        to_root.text = from_root.text
        to_root.tail = from_root.tail
        if isinstance(tag, basestring): # skip Comments etc.
            self.copyChildren(from_root, to_root)
        return to_root


class TreeReplicatorMaker(object):
    """Fast tree mass replication.

    Original implementation by Fredrik Lundh.

    Note that the fastest way to deep copy an lxml XML tree is to use
    the ``deepcopy()`` function from the standard Python ``copy``
    module.
    """
    def __init__(ET_impl, makeelement=None):
        if makeelement is None:
            makeelement = ET_impl.Element
        self.functions = {
            "Element"    : makeelement,
            "SubElement" : ET_impl.SubElement,
            "Comment"    : ET_impl.Comment,
            "PI"         : ET_impl.PI,
            }

    def make_clone_factory(self, elem):
        if hasattr(elem, 'getroot'):
            elem = elem.getroot()
        def generate_elem(append, elem, level):
            var = "e" + str(level)
            arg = repr(elem.tag)
            attrib = elem.attrib
            if attrib:
                arg += ", **%r" % attrib
            if level == 1:
                append(" e1 = Element(%s)" % arg)
            else:
                append(" %s = SubElement(e%d, %s)" % (var, level-1, arg))
            text = elem.text
            if text:
                append(" %s.text = %r" % (var, text))
            tail = elem.tail
            if tail:
                append(" %s.tail = %r" % (var, tail))
            for e in elem:
                generate_elem(append, e, level+1)
        # generate code for a function that creates a tree
        output = ["def element_factory():"]
        generate_elem(output.append, elem, 1)
        output.append(" return e1")
        # setup global function namespace
        # create function object
        namespace = self.functions.copy()
        exec "\n".join(output) in namespace
        return namespace["element_factory"]
