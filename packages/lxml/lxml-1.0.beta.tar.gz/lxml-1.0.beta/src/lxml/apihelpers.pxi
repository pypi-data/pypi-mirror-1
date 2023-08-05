# Private helper functions for API functions

cdef void displayNode(xmlNode* c_node, indent):
    # to help with debugging
    cdef xmlNode* c_child
    print indent * ' ', <int>c_node
    c_child = c_node.children
    while c_child is not NULL:
        displayNode(c_child, indent + 1)
        c_child = c_child.next

cdef _Document _documentOrRaise(object input):
    cdef _Document doc
    doc = _documentOf(input)
    if doc is None:
        raise TypeError, "Invalid input object: %s" % type(input)
    else:
        return doc

cdef _Document _documentOf(object input):
    # call this to get the document of a
    # _Document, _ElementTree or _NodeBase object
    if isinstance(input, _ElementTree):
        return (<_ElementTree>input)._doc
    elif isinstance(input, _NodeBase):
        return (<_NodeBase>input)._doc
    elif isinstance(input, _Document):
        return <_Document>input
    else:
        return None

cdef _NodeBase _rootNodeOf(object input):
    # call this to get the root node of a
    # _Document, _ElementTree or _NodeBase object
    if isinstance(input, _ElementTree):
        return (<_ElementTree>input)._context_node
    elif isinstance(input, _NodeBase):
        return <_NodeBase>input
    elif isinstance(input, _Document):
        return (<_Document>input).getroot()
    else:
        return None

cdef xmlDoc* _fakeRootDoc(xmlDoc* c_base_doc, xmlNode* c_node):
    # build a temporary document that has the given node as root node
    # note that copy and original must not be modified during its lifetime!!
    # always call _destroyFakeDoc() after use!
    cdef xmlNode* c_child
    cdef xmlNode* c_root
    cdef xmlDoc*  c_doc
    c_root = tree.xmlDocGetRootElement(c_base_doc)
    if c_root == c_node:
        # already the root node
        return c_base_doc

    c_doc  = tree.xmlCopyDoc(c_base_doc, 0)        # non recursive!
    c_root = tree.xmlDocCopyNode(c_node, c_doc, 2) # non recursive!

    c_root.children = c_node.children
    c_root.last = c_node.last
    c_root.next = c_root.prev = c_root.parent = NULL

    # store original node
    c_root._private = c_node

    # divert parent pointers of children
    c_child = c_root.children
    while c_child is not NULL:
        c_child.parent = c_root
        c_child = c_child.next

    c_doc.children = c_root
    return c_doc

cdef void _destroyFakeDoc(xmlDoc* c_base_doc, xmlDoc* c_doc):
    # delete a temporary document
    cdef xmlNode* c_child
    cdef xmlNode* c_parent
    cdef xmlNode* c_root
    if c_doc != c_base_doc:
        c_root = tree.xmlDocGetRootElement(c_doc)

        # restore parent pointers of children
        c_parent = <xmlNode*>c_root._private
        c_child = c_root.children
        while c_child is not NULL:
            c_child.parent = c_parent
            c_child = c_child.next

        # prevent recursive removal of children
        c_root.children = c_root.last = c_root._private = NULL
        tree.xmlFreeDoc(c_doc)

cdef object _attributeValue(xmlNode* c_element, xmlNode* c_attrib_node):
    cdef char* value
    if c_attrib_node.ns is NULL or c_attrib_node.ns.href is NULL:
        value = tree.xmlGetNoNsProp(c_element, c_attrib_node.name)
    else:
        value = tree.xmlGetNsProp(c_element, c_attrib_node.name,
                                  c_attrib_node.ns.href)
    return funicode(value)

cdef object __REPLACE_XML_ENCODING
__REPLACE_XML_ENCODING = re.compile(
    r'^(\s*<\?\s*xml[^>]+)\s+encoding\s*=\s*"[^"]*"\s*', re.U).sub

cdef object _stripEncodingDeclaration(object xml_string):
    # this is a hack to remove the XML encoding declaration from unicode
    return __REPLACE_XML_ENCODING(r'\g<1>', xml_string)

cdef object _stripDeclaration(object xml_string):
    # this is a hack to remove the XML declaration when we encode to UTF-8
    xml_string = xml_string.strip()
    if xml_string[:5] == '<?xml':
        i = xml_string.find('?>')
        if i != -1:
            i = i + 2
            while xml_string[i:i+1] in '\n\r ':
                i = i+1
            xml_string = xml_string[i:]
    return xml_string

cdef _collectText(xmlNode* c_node):
    """Collect all text nodes and return them as a unicode string.

    Start collecting at c_node.
    
    If there was no text to collect, return None
    """
    cdef Py_ssize_t scount
    cdef char* text
    cdef xmlNode* c_node_cur
    # check for multiple text nodes
    scount = 0
    text = NULL
    c_node_cur = c_node
    while c_node_cur is not NULL and c_node_cur.type == tree.XML_TEXT_NODE:
        if c_node_cur.content[0] != c'\0':
            text = c_node_cur.content
            scount = scount + 1
        c_node_cur = c_node_cur.next

    # handle two most common cases first
    if text is NULL:
        return None
    if scount == 1:
        return funicode(text)

    # the rest is not performance critical anymore
    result = ''
    while c_node is not NULL and c_node.type == tree.XML_TEXT_NODE:
        result = result + c_node.content
        c_node = c_node.next
    return funicode(result)

cdef _removeText(xmlNode* c_node):
    """Remove all text nodes.

    Start removing at c_node.
    """
    cdef xmlNode* c_next
    while c_node is not NULL and c_node.type == tree.XML_TEXT_NODE:
        c_next = c_node.next
        tree.xmlUnlinkNode(c_node)
        # XXX cannot safely free in case of direct text node proxies..
        tree.xmlFreeNode(c_node)
        c_node = c_next

cdef xmlNode* _findChild(xmlNode* c_node, Py_ssize_t index):
    if index < 0:
        return _findChildBackwards(c_node, -index - 1)
    else:
        return _findChildForwards(c_node, index)
    
cdef xmlNode* _findChildForwards(xmlNode* c_node, Py_ssize_t index):
    """Return child element of c_node with index, or return NULL if not found.
    """
    cdef xmlNode* c_child
    cdef Py_ssize_t c
    c_child = c_node.children
    c = 0
    while c_child is not NULL:
        if _isElement(c_child):
            if c == index:
                return c_child
            c = c + 1
        c_child = c_child.next
    return NULL

cdef xmlNode* _findChildBackwards(xmlNode* c_node, Py_ssize_t index):
    """Return child element of c_node with index, or return NULL if not found.
    Search from the end.
    """
    cdef xmlNode* c_child
    cdef Py_ssize_t c
    c_child = c_node.last
    c = 0
    while c_child is not NULL:
        if _isElement(c_child):
            if c == index:
                return c_child
            c = c + 1
        c_child = c_child.prev
    return NULL
    
cdef xmlNode* _nextElement(xmlNode* c_node):
    """Given a node, find the next sibling that is an element.
    """
    c_node = c_node.next
    while c_node is not NULL:
        if _isElement(c_node):
            return c_node
        c_node = c_node.next
    return NULL

cdef xmlNode* _previousElement(xmlNode* c_node):
    """Given a node, find the next sibling that is an element.
    """
    c_node = c_node.prev
    while c_node is not NULL:
        if _isElement(c_node):
            return c_node
        c_node = c_node.prev
    return NULL

cdef xmlNode* _findDepthFirstInDescendents(xmlNode* c_node,
                                           char* c_href, char* c_name):
    if c_node is NULL:
        return NULL
    c_node = c_node.children
    if c_node is NULL:
        return NULL
    if not _isElement(c_node):
        c_node = _nextElement(c_node)
    return _findDepthFirstInFollowing(c_node, c_href, c_name)

cdef xmlNode* _findDepthFirstInFollowingSiblings(xmlNode* c_node,
                                                 char* c_href, char* c_name):
    if c_node is NULL:
        return NULL
    c_node = _nextElement(c_node)
    return _findDepthFirstInFollowing(c_node, c_href, c_name)

cdef xmlNode* _findDepthFirstInFollowing(xmlNode* c_node,
                                         char* c_href, char* c_name):
    """Find the next matching node by traversing:
    1) the node itself
    2) its descendents
    3) its following siblings.
    """
    cdef xmlNode* c_child
    if c_name is NULL:
        # always match
        return c_node
    while c_node is not NULL:
        if _tagMatches(c_node, c_href, c_name):
            return c_node
        if c_node.children is not NULL:
            c_child = _findDepthFirstInFollowing(c_node.children, c_href, c_name)
            if c_child is not NULL:
                return c_child
        c_node = _nextElement(c_node)
    return NULL

cdef int _tagMatches(xmlNode* c_node, char* c_href, char* c_name):
    if c_name is NULL:
        # always match
        return 1
    if c_href is NULL:
        if c_node.ns is not NULL and c_node.ns.href is not NULL:
            return 0
        return cstd.strcmp(c_node.name, c_name) == 0
    elif c_node.ns is NULL or c_node.ns.href is NULL:
        return 0
    else:
        return cstd.strcmp(c_node.name, c_name) == 0 and \
               cstd.strcmp(c_node.ns.href, c_href) == 0

cdef void _removeNode(xmlNode* c_node):
    """Unlink and free a node and subnodes if possible.
    """
    tree.xmlUnlinkNode(c_node)
    attemptDeallocation(c_node)

cdef void _moveTail(xmlNode* c_tail, xmlNode* c_target):
    cdef xmlNode* c_next
    # tail support: look for any text nodes trailing this node and 
    # move them too
    while c_tail is not NULL and c_tail.type == tree.XML_TEXT_NODE:
        c_next = c_tail.next
        tree.xmlUnlinkNode(c_tail)
        tree.xmlAddNextSibling(c_target, c_tail)
        c_target = c_tail
        c_tail = c_next

cdef xmlNode* _deleteSlice(xmlNode* c_node, Py_ssize_t start, Py_ssize_t stop):
    """Delete slice, starting with c_node, start counting at start, end at stop.
    """
    cdef xmlNode* c_next
    cdef Py_ssize_t c
    if c_node is NULL:
        return NULL
    # now start deleting nodes
    c = start
    while c_node is not NULL and c < stop:
        c_next = c_node.next
        if _isElement(c_node):
            _removeText(c_node.next)
            c_next = c_node.next
            _removeNode(c_node)
            c = c + 1
        c_node = c_next
    return c_node

cdef int isutf8(char* s):
    cdef char c
    c = s[0]
    while c != c'\0':
        if c & 0x80:
            return 1
        s = s + 1
        c = s[0]
    return 0

cdef object funicode(char* s):
    if isutf8(s):
        return python.PyUnicode_DecodeUTF8(s, cstd.strlen(s), NULL)
    return python.PyString_FromString(s)

cdef object _utf8(object s):
    if python.PyString_Check(s):
        assert not isutf8(_cstr(s)), "All strings must be Unicode or ASCII"
        return s
    elif python.PyUnicode_Check(s):
        return python.PyUnicode_AsUTF8String(s)
    else:
        raise TypeError, "Argument must be string or unicode."

cdef _getNsTag(tag):
    """Given a tag, find namespace URI and tag name.
    Return None for NS uri if no namespace URI available.
    """
    cdef char* c_tag
    cdef char* c_pos
    cdef int nslen
    if isinstance(tag, QName):
        tag = (<QName>tag).text
    tag = _utf8(tag)
    c_tag = _cstr(tag)
    if c_tag[0] == c'{':
        c_pos = tree.xmlStrchr(c_tag+1, c'}')
        if c_pos is NULL:
            raise ValueError, "Invalid tag name"
        nslen = c_pos - c_tag - 1
        ns  = python.PyString_FromStringAndSize(c_tag+1, nslen)
        tag = python.PyString_FromString(c_pos+1)
    else:
        ns = None
    return ns, tag
    
cdef object _namespacedName(xmlNode* c_node):
    cdef char* href
    cdef char* name
    name = c_node.name
    if c_node.ns is NULL or c_node.ns.href is NULL:
        return funicode(name)
    else:
        href = c_node.ns.href
        s = python.PyString_FromFormat("{%s}%s", href, name)
        if isutf8(href) or isutf8(name):
            return python.PyUnicode_FromEncodedObject(s, 'UTF-8', NULL)
        else:
            return s

cdef _getFilenameForFile(source):
    """Given a Python File or Gzip object, give filename back.

    Returns None if not a file object.
    """
    # file instances have a name attribute
    if hasattr(source, 'name'):
        return source.name
    # gzip file instances have a filename attribute
    if hasattr(source, 'filename'):
        return source.filename
    # urllib2
    if hasattr(source, 'geturl'):
        return source.geturl()
    return None

cdef void changeDocumentBelow(_NodeBase node, _Document doc, int recursive):
    """For a node and all nodes below, change document.

    A node can change document in certain operations as an XML
    subtree can move. This updates all possible proxies in the
    tree below (including the current node). It also reconciliates
    namespaces so they're correct inside the new environment.
    """
    if recursive:
        changeDocumentBelowHelper(node._c_node, doc)
    tree.xmlReconciliateNs(doc._c_doc, node._c_node)
    
cdef void changeDocumentBelowHelper(xmlNode* c_node, _Document doc):
    cdef ProxyRef* ref
    cdef xmlNode* c_current
    cdef xmlAttr* c_attr_current
    cdef _NodeBase proxy

    if c_node is NULL:
        return
    # different _c_doc
    c_node.doc = doc._c_doc
    
    if c_node._private is not NULL:
        ref = <ProxyRef*>c_node._private
        while ref is not NULL:
            proxy = <_NodeBase>ref.proxy
            proxy._doc = doc
            ref = ref.next

    # adjust all children
    c_current = c_node.children
    while c_current is not NULL:
        changeDocumentBelowHelper(c_current, doc)
        c_current = c_current.next
        
    # adjust all attributes
    c_attr_current = c_node.properties
    while c_attr_current is not NULL:
        changeDocumentBelowHelper(c_current, doc)
        c_attr_current = c_attr_current.next
