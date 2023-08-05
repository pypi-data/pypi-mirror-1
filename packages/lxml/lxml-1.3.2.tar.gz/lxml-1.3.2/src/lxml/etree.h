#ifndef __HAS_PYX_etree
#define __HAS_PYX_etree
#ifdef __cplusplus
#define __PYX_EXTERN_C extern "C"
#else
#define __PYX_EXTERN_C extern
#endif
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlDocumentType;

struct LxmlDocument {
  PyObject_HEAD
  struct __pyx_vtabstruct_5etree__Document *__pyx_vtab;
  int _ns_counter;
  xmlDoc (*_c_doc);
  struct __pyx_obj_5etree__BaseParser *_parser;
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementType;

struct LxmlElement {
  PyObject_HEAD
  PyObject (*_gc_doc);
  struct LxmlDocument *_doc;
  xmlNode (*_c_node);
  PyObject *_tag;
  PyObject *_attrib;
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementTreeType;

struct LxmlElementTree {
  PyObject_HEAD
  struct __pyx_vtabstruct_5etree__ElementTree *__pyx_vtab;
  struct LxmlDocument *_doc;
  struct LxmlElement *_context_node;
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementTagMatcherType;

struct LxmlElementTagMatcher {
  PyObject_HEAD
  struct __pyx_vtabstruct_5etree__ElementTagMatcher *__pyx_vtab;
  PyObject *_pystrings;
  int _node_type;
  char (*_href);
  char (*_name);
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementIteratorType;

struct LxmlElementIterator {
  struct LxmlElementTagMatcher __pyx_base;
  struct LxmlElement *_node;
  xmlNode (*((*_next_element)(xmlNode (*))));
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementBaseType;

struct LxmlElementBase {
  struct LxmlElement __pyx_base;
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementClassLookupType;

struct LxmlElementClassLookup {
  PyObject_HEAD
  PyObject *((*_lookup_function)(PyObject *,struct LxmlDocument *,xmlNode (*)));
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlFallbackElementClassLookupType;

struct LxmlFallbackElementClassLookup {
  struct LxmlElementClassLookup __pyx_base;
  struct __pyx_vtabstruct_5etree_FallbackElementClassLookup *__pyx_vtab;
  struct LxmlElementClassLookup *fallback;
  PyObject *((*_fallback_function)(PyObject *,struct LxmlDocument *,xmlNode (*)));
};
static void ((*appendChild)(struct LxmlElement *,struct LxmlElement *));
static PyObject *((*attributeValue)(xmlNode (*),xmlAttr (*)));
static PyObject *((*attributeValueFromNsName)(xmlNode (*),char (*),char (*)));
static PyObject *((*callLookupFallback)(struct LxmlFallbackElementClassLookup *,struct LxmlDocument *,xmlNode (*)));
static PyObject *((*collectAttributes)(xmlNode (*),int ));
static struct LxmlElement *((*deepcopyNodeToDocument)(struct LxmlDocument *,xmlNode (*)));
static int ((*delAttribute)(struct LxmlElement *,PyObject *));
static int ((*delAttributeFromNsName)(xmlNode (*),char (*),char (*)));
static struct LxmlDocument *((*documentOrRaise)(PyObject *));
static struct LxmlElement *((*elementFactory)(struct LxmlDocument *,xmlNode (*)));
static struct LxmlElementTree *((*elementTreeFactory)(struct LxmlElement *));
static xmlNode (*((*findChild)(xmlNode (*),Py_ssize_t )));
static xmlNode (*((*findChildBackwards)(xmlNode (*),Py_ssize_t )));
static xmlNode (*((*findChildForwards)(xmlNode (*),Py_ssize_t )));
static xmlNs (*((*findOrBuildNodeNs)(struct LxmlDocument *,xmlNode (*),char (*))));
static PyObject *((*getAttributeValue)(struct LxmlElement *,PyObject *,PyObject *));
static PyObject *((*getNsTag)(PyObject *));
static void ((*initTagMatch)(struct LxmlElementTagMatcher *,PyObject *));
static void ((*iteratorStoreNext)(struct LxmlElementIterator *,struct LxmlElement *));
static PyObject *((*iterattributes)(struct LxmlElement *,int ));
static PyObject *((*lookupDefaultElementClass)(PyObject *,PyObject *,xmlNode (*)));
static PyObject *((*lookupNamespaceElementClass)(PyObject *,PyObject *,xmlNode (*)));
static struct LxmlElement *((*makeElement)(PyObject *,struct LxmlDocument *,PyObject *,PyObject *,PyObject *,PyObject *,PyObject *));
static PyObject *((*namespacedName)(xmlNode (*)));
static PyObject *((*namespacedNameFromNsName)(char (*),char (*)));
static struct LxmlElementTree *((*newElementTree)(struct LxmlElement *,PyObject *));
static xmlNode (*((*nextElement)(xmlNode (*))));
static xmlNode (*((*previousElement)(xmlNode (*))));
static PyObject *((*pyunicode)(char (*)));
static struct LxmlElement *((*rootNodeOrRaise)(PyObject *));
static int ((*setAttributeValue)(struct LxmlElement *,PyObject *,PyObject *));
static void ((*setElementClassLookupFunction)(PyObject *((*)(PyObject *,struct LxmlDocument *,xmlNode (*))),PyObject *));
static int ((*setNodeText)(xmlNode (*),PyObject *));
static int ((*setTailText)(xmlNode (*),PyObject *));
static int ((*tagMatches)(xmlNode (*),char (*),char (*)));
static PyObject *((*tailOf)(xmlNode (*)));
static PyObject *((*textOf)(xmlNode (*)));
static PyObject *((*utf8)(PyObject *));
static struct {char *s; void **p;} _etree_API[] = {
  {"appendChild", &appendChild},
  {"attributeValue", &attributeValue},
  {"attributeValueFromNsName", &attributeValueFromNsName},
  {"callLookupFallback", &callLookupFallback},
  {"collectAttributes", &collectAttributes},
  {"deepcopyNodeToDocument", &deepcopyNodeToDocument},
  {"delAttribute", &delAttribute},
  {"delAttributeFromNsName", &delAttributeFromNsName},
  {"documentOrRaise", &documentOrRaise},
  {"elementFactory", &elementFactory},
  {"elementTreeFactory", &elementTreeFactory},
  {"findChild", &findChild},
  {"findChildBackwards", &findChildBackwards},
  {"findChildForwards", &findChildForwards},
  {"findOrBuildNodeNs", &findOrBuildNodeNs},
  {"getAttributeValue", &getAttributeValue},
  {"getNsTag", &getNsTag},
  {"initTagMatch", &initTagMatch},
  {"iteratorStoreNext", &iteratorStoreNext},
  {"iterattributes", &iterattributes},
  {"lookupDefaultElementClass", &lookupDefaultElementClass},
  {"lookupNamespaceElementClass", &lookupNamespaceElementClass},
  {"makeElement", &makeElement},
  {"namespacedName", &namespacedName},
  {"namespacedNameFromNsName", &namespacedNameFromNsName},
  {"newElementTree", &newElementTree},
  {"nextElement", &nextElement},
  {"previousElement", &previousElement},
  {"pyunicode", &pyunicode},
  {"rootNodeOrRaise", &rootNodeOrRaise},
  {"setAttributeValue", &setAttributeValue},
  {"setElementClassLookupFunction", &setElementClassLookupFunction},
  {"setNodeText", &setNodeText},
  {"setTailText", &setTailText},
  {"tagMatches", &tagMatches},
  {"tailOf", &tailOf},
  {"textOf", &textOf},
  {"utf8", &utf8},
  {0, 0}
};

/* Return -1 and set exception on error, 0 on success. */
static int
import_etree(PyObject *module)
{
    if (module != NULL)
    {
        int (*init)(struct {const char *s; const void **p;}*);
        PyObject* c_api_init;

        c_api_init = PyObject_GetAttrString(module,
                                            "_import_c_api");
        if (!c_api_init)
            return -1;
        if (!PyCObject_Check(c_api_init))
        {
            Py_DECREF(c_api_init);
            PyErr_SetString(PyExc_RuntimeError,
                "etree module provided an invalid C-API reference");
            return -1;
        }

        init = PyCObject_AsVoidPtr(c_api_init);
        Py_DECREF(c_api_init);
        if (!init)
        {
            PyErr_SetString(PyExc_RuntimeError,
                "etree module returned NULL pointer for C-API init function");
            return -1;
        }

        if (init(_etree_API))
            return -1;
    }
    return 0;
}
PyMODINIT_FUNC initetree(void);
#endif /* __HAS_PYX_etree */
