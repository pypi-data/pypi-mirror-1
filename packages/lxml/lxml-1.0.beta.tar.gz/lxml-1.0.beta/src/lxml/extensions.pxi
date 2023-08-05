# supports for extension functions in XPath and XSLT

cimport xpath

class XPathError(LxmlError):
    pass

class XPathFunctionError(XPathError):
    pass

class XPathResultError(XPathError):
    pass

################################################################################
# Base class for XSLT and XPath evaluation contexts: functions, namespaces, ...

cdef class _BaseContext:
    cdef xpath.xmlXPathContext* _xpathCtxt
    cdef xpath.xmlXPathFuncLookupFunc _ext_lookup_function
    cdef _Document _doc
    cdef object _extensions
    cdef object _namespaces
    cdef object _utf_refs
    cdef object _function_cache
    cdef object _function_cache_ns
    cdef object _called_function
    # for exception handling and temporary reference keeping:
    cdef _TempStore _temp_refs
    cdef _ExceptionContext _exc

    def __init__(self, namespaces, extensions):
        self._xpathCtxt = NULL
        self._utf_refs = {}
        self._function_cache = {}
        self._function_cache_ns = {}
        self._called_function = None

        if extensions is not None:
            # convert extensions to UTF-8
            if python.PyDict_Check(extensions):
                extensions = (extensions,)
            # format: [ {(ns,name):function} ] -> {(ns_utf,name_utf):function}
            new_extensions = {}
            for extension in extensions:
                for (ns_uri, name), function in extension.items():
                    ns_utf   = self._to_utf(ns_uri)
                    name_utf = self._to_utf(name)
                    python.PyDict_SetItem(
                        new_extensions, (ns_utf, name_utf), function)
            extensions = new_extensions or None

        self._doc        = None
        self._exc        = _ExceptionContext()
        self._extensions = extensions
        self._namespaces = namespaces
        self._temp_refs = _TempStore()

    cdef object _to_utf(self, s):
        "Convert to UTF-8 and keep a reference to the encoded string"
        cdef python.PyObject* dict_result
        if s is None:
            return None
        dict_result = python.PyDict_GetItem(self._utf_refs, s)
        if dict_result is not NULL:
            return <object>dict_result
        utf = _utf8(s)
        python.PyDict_SetItem(self._utf_refs, s, utf)
        return utf

    cdef void _set_xpath_context(self, xpath.xmlXPathContext* xpathCtxt):
        self._xpathCtxt = xpathCtxt
        xpathCtxt.userData = <void*>self

    cdef _register_context(self, _Document doc):
        self._doc = doc
        self._exc.clear()
        python.PyDict_Clear(self._function_cache)
        python.PyDict_Clear(self._function_cache_ns)
        namespaces = self._namespaces
        if namespaces is not None:
            self.registerNamespaces(namespaces)
        xpath.xmlXPathRegisterFuncLookup(
            self._xpathCtxt, self._ext_lookup_function, <python.PyObject*>self)

    cdef _unregister_context(self):
        xpath.xmlXPathRegisteredNsCleanup(self._xpathCtxt)
        self._free_context()

    cdef _free_context(self):
        python.PyDict_Clear(self._utf_refs)
        self._doc = None
        if self._xpathCtxt is not NULL:
            self._xpathCtxt.userData = NULL
            self._xpathCtxt = NULL

    # namespaces (internal UTF-8 methods with leading '_')

    def addNamespace(self, prefix, uri):
        if self._namespaces is None:
            self._namespaces = {}
        python.PyDict_SetItem(self._namespaces, prefix, uri)

    def registerNamespaces(self, namespaces):
        for prefix, uri in namespaces.items():
            self.registerNamespace(prefix, uri)
    
    def registerNamespace(self, prefix, ns_uri):
        prefix_utf = self._to_utf(prefix)
        ns_uri_utf = self._to_utf(ns_uri)
        xpath.xmlXPathRegisterNs(self._xpathCtxt, prefix_utf, ns_uri_utf)
    
    # extension functions

    cdef int _prepare_function_call(self, char* c_ns_uri, char* c_name):
        """Find an extension function and store it in 'self._called_function'.
        This is absolutely performance-critical for XPath/XSLT!
        Return 1 if it was found, 0 otherwise.
        Parameters: c_ns_uri may be NULL, c_name must not be NULL
        """
        cdef python.PyObject* c_dict
        cdef python.PyObject* dict_result
        if c_ns_uri is NULL:
            c_dict = <python.PyObject*>self._function_cache
        else:
            c_dict = python.PyDict_GetItemString(
                self._function_cache_ns, c_ns_uri)

        if c_dict is not NULL:
            d = <object>c_dict
            dict_result = python.PyDict_GetItemString(d, c_name)
            if dict_result is not NULL:
                function = <object>dict_result
                self._called_function = function
                return function is not None
        else:
            d = {}
            python.PyDict_SetItem(self._function_cache_ns, ns_uri_utf, d)

        # first time we look up this function, so the rest is less critical
        if c_ns_uri is not NULL:
            ns_uri_utf = c_ns_uri
        name_utf = c_name

        if self._extensions is not None:
            dict_result = python.PyDict_GetItem(
                self._extensions, (ns_uri_utf, name_utf))
        else:
            dict_result = NULL
        if dict_result is not NULL:
            function = <object>dict_result
        else:
            function = _find_extension(ns_uri_utf, name_utf)

        # we also store None values here to make sure we remember
        python.PyDict_SetItem(d, name_utf, function)
        self._called_function = function
        return function is not None

    # Python reference keeping during XPath function evaluation

    cdef _release_temp_refs(self):
        "Free temporarily referenced objects from this context."
        self._temp_refs.clear()
        
    cdef _hold(self, obj):
        """A way to temporarily hold references to nodes in the evaluator.

        This is needed because otherwise nodes created in XPath extension
        functions would be reference counted too soon, during the XPath
        evaluation.  This is most important in the case of exceptions.
        """
        cdef _NodeBase element
        if isinstance(obj, _NodeBase):
            obj = (obj,)
        elif not python.PySequence_Check(obj):
            return
        for o in obj:
            if isinstance(o, _NodeBase):
                element = <_NodeBase>o
                #print "Holding element:", <int>element._c_node
                self._temp_refs.add(element)
                #print "Holding document:", <int>element._doc._c_doc
                self._temp_refs.add(element._doc)


def Extension(module, function_mapping, ns=None):
    functions = {}
    if python.PyDict_Check(function_mapping):
        for function_name, xpath_name in function_mapping.items():
            python.PyDict_SetItem(functions, (ns, xpath_name),
                                  getattr(module, function_name))
    else:
        if function_mapping is None:
            function_mapping = []
            for name in dir(module):
                if not name.startswith('_'):
                    python.PyList_Append(function_mapping, name)
        for function_name in function_mapping:
            python.PyDict_SetItem(functions, (ns, function_name),
                                  getattr(module, function_name))
    return functions


################################################################################
# helper functions

cdef xpath.xmlXPathFunction _function_check(void* ctxt,
                                            char* c_name, char* c_ns_uri):
    "Module level lookup function for XPath/XSLT functions"
    cdef _BaseContext context
    context = <_BaseContext>ctxt
    if context._prepare_function_call(c_ns_uri, c_name):
        return _call_prepared_function
    else:
        return NULL

cdef xpath.xmlXPathObject* _wrapXPathObject(object obj) except NULL:
    cdef xpath.xmlNodeSet* resultSet
    cdef _NodeBase node
    if python.PyUnicode_Check(obj):
        obj = _utf8(obj)
    if python.PyString_Check(obj):
        return xpath.xmlXPathNewCString(_cstr(obj))
    if python.PyBool_Check(obj):
        return xpath.xmlXPathNewBoolean(obj)
    if python.PyNumber_Check(obj):
        return xpath.xmlXPathNewFloat(obj)
    if obj is None:
        obj = ()
    elif isinstance(obj, _NodeBase):
        obj = (obj,)
    if python.PySequence_Check(obj):
        resultSet = xpath.xmlXPathNodeSetCreate(NULL)
        for element in obj:
            if isinstance(element, _NodeBase):
                node = <_NodeBase>element
                xpath.xmlXPathNodeSetAdd(resultSet, node._c_node)
            else:
                xpath.xmlXPathFreeNodeSet(resultSet)
                raise XPathResultError, "This is not a node: %s" % element
        return xpath.xmlXPathWrapNodeSet(resultSet)
    else:
        raise XPathResultError, "Unknown return type: %s" % obj
    return NULL

cdef object _unwrapXPathObject(xpath.xmlXPathObject* xpathObj,
                               _Document doc):
    if xpathObj.type == xpath.XPATH_UNDEFINED:
        raise XPathResultError, "Undefined xpath result"
    elif xpathObj.type == xpath.XPATH_NODESET:
        return _createNodeSetResult(xpathObj, doc)
    elif xpathObj.type == xpath.XPATH_BOOLEAN:
        return python.PyBool_FromLong(xpathObj.boolval)
    elif xpathObj.type == xpath.XPATH_NUMBER:
        return xpathObj.floatval
    elif xpathObj.type == xpath.XPATH_STRING:
        return funicode(xpathObj.stringval)
    elif xpathObj.type == xpath.XPATH_POINT:
        raise NotImplementedError
    elif xpathObj.type == xpath.XPATH_RANGE:
        raise NotImplementedError
    elif xpathObj.type == xpath.XPATH_LOCATIONSET:
        raise NotImplementedError
    elif xpathObj.type == xpath.XPATH_USERS:
        raise NotImplementedError
    elif xpathObj.type == xpath.XPATH_XSLT_TREE:
        raise NotImplementedError
    else:
        raise XPathResultError, "Unknown xpath result %s" % str(xpathObj.type)

cdef object _createNodeSetResult(xpath.xmlXPathObject* xpathObj, _Document doc):
    cdef xmlNode* c_node
    cdef char* s
    cdef int i
    result = []
    if xpathObj.nodesetval is NULL:
        return result
    for i from 0 <= i < xpathObj.nodesetval.nodeNr:
        c_node = xpathObj.nodesetval.nodeTab[i]
        if _isElement(c_node):
            if c_node.doc != doc._c_doc:
                # XXX: works, but maybe not always the right thing to do?
                # XPath: only runs when extensions create or copy trees
                #        -> we store Python refs to these, so that is OK
                # XSLT: can it leak when merging trees from multiple sources?
                c_node = tree.xmlDocCopyNode(c_node, doc._c_doc, 1)
            value = _elementFactory(doc, c_node)
        elif c_node.type == tree.XML_TEXT_NODE:
            value = funicode(c_node.content)
        elif c_node.type == tree.XML_ATTRIBUTE_NODE:
            s = tree.xmlNodeGetContent(c_node)
            value = funicode(s)
            tree.xmlFree(s)
        else:
            print "Not yet implemented result node type:", c_node.type
            raise NotImplementedError
        python.PyList_Append(result, value)
    return result

cdef void _freeXPathObject(xpath.xmlXPathObject* xpathObj):
    """Free the XPath object, but *never* free the *content* of node sets.
    Python dealloc will do that for us.
    """
    if xpathObj.nodesetval is not NULL:
        xpath.xmlXPathFreeNodeSet(xpathObj.nodesetval)
        xpathObj.nodesetval = NULL
    xpath.xmlXPathFreeObject(xpathObj)

cdef void _xpath_function_call(xpath.xmlXPathParserContext* ctxt, int nargs):
    cdef xpath.xmlXPathContext* rctxt
    cdef _BaseContext context
    rctxt = ctxt.context
    context = <_BaseContext>(rctxt.userData)
    if context._prepare_function_call(rctxt.functionURI, rctxt.function):
        _extension_function_call(context, ctxt, nargs)
    else:
        if rctxt.functionURI is not NULL:
            fref = "{%s}%s" % (rctxt.functionURI, rctxt.function)
        else:
            fref = rctxt.function
        xpath.xmlXPathErr(ctxt, xpath.XPATH_EXPR_ERROR)
        exception = XPathFunctionError("XPath function '%s' not found" % fref)
        context._exc._store_exception(exception)

cdef void _call_prepared_function(xpath.xmlXPathParserContext* ctxt, int nargs):
    cdef xpath.xmlXPathContext* rctxt
    cdef _BaseContext context
    rctxt = ctxt.context
    context = <_BaseContext>(rctxt.userData)
    _extension_function_call(context, ctxt, nargs)

cdef void _extension_function_call(_BaseContext context,
                                   xpath.xmlXPathParserContext* ctxt, int nargs):
    cdef _NodeBase node
    cdef _Document doc
    cdef xpath.xmlXPathObject* obj
    cdef int i
    doc = context._doc
    try:
        args = []
        for i from 0 <= i < nargs:
            o = _unwrapXPathObject(xpath.valuePop(ctxt), doc)
            python.PyList_Append(args, o)
        python.PyList_Reverse(args)

        res = context._called_function(None, *args)
        # wrap result for XPath consumption
        obj = _wrapXPathObject(res)
        # prevent Python from deallocating elements handed to libxml2
        context._hold(res)
        xpath.valuePush(ctxt, obj)
    except:
        xpath.xmlXPathErr(ctxt, xpath.XPATH_EXPR_ERROR)
        context._exc._store_raised()
