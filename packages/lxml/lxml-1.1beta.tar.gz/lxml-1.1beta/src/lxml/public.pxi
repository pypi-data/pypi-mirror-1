# Public C API for lxml.etree

cdef public _ElementTree elementTreeFactory(_NodeBase context_node):
    return newElementTree(context_node, _ElementTree)

cdef public _ElementTree newElementTree(_NodeBase context_node,
                                        object baseclass):
    if <void*>context_node is NULL or context_node is None:
        raise TypeError

    return _newElementTree(context_node._doc, context_node, baseclass)

cdef public _Element elementFactory(_Document doc, xmlNode* c_node):
    if c_node is NULL or doc is None:
        raise TypeError
    return _elementFactory(doc, c_node)

cdef public int tagMatches(xmlNode* c_node, char* c_href, char* c_name):
    if c_node is NULL:
        return -1
    return _tagMatches(c_node, c_href, c_name)
