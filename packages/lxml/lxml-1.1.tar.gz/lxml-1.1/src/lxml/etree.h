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
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlNodeBaseType;

struct LxmlNodeBase {
  PyObject_HEAD
  struct LxmlDocument *_doc;
  xmlNode (*_c_node);
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementTreeType;

struct LxmlElementTree {
  PyObject_HEAD
  struct __pyx_vtabstruct_5etree__ElementTree *__pyx_vtab;
  struct LxmlDocument *_doc;
  struct LxmlNodeBase *_context_node;
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementType;

struct LxmlElement {
  struct LxmlNodeBase __pyx_base;
  PyObject *_tag;
  PyObject *_attrib;
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementTagMatcherType;

struct LxmlElementTagMatcher {
  PyObject_HEAD
  struct __pyx_vtabstruct_5etree__ElementTagMatcher *__pyx_vtab;
  PyObject *_pystrings;
  char (*_href);
  char (*_name);
};
__PYX_EXTERN_C DL_IMPORT(PyTypeObject) LxmlElementIteratorType;

struct LxmlElementIterator {
  struct LxmlElementTagMatcher __pyx_base;
  struct LxmlNodeBase *_node;
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
static struct LxmlElement *((*deepcopyNodeToDocument)(struct LxmlDocument *,xmlNode (*)));
static struct LxmlElementTree *((*elementTreeFactory)(struct LxmlNodeBase *));
static struct LxmlElementTree *((*newElementTree)(struct LxmlNodeBase *,PyObject *));
static struct LxmlElement *((*elementFactory)(struct LxmlDocument *,xmlNode (*)));
static void ((*setElementClassLookupFunction)(PyObject *((*)(PyObject *,struct LxmlDocument *,xmlNode (*))),PyObject *));
static PyObject *((*lookupDefaultElementClass)(PyObject *,PyObject *,xmlNode (*)));
static PyObject *((*lookupNamespaceElementClass)(PyObject *,PyObject *,xmlNode (*)));
static PyObject *((*callLookupFallback)(struct LxmlFallbackElementClassLookup *,struct LxmlDocument *,xmlNode (*)));
static int ((*tagMatches)(xmlNode (*),char (*),char (*)));
static struct LxmlDocument *((*documentOrRaise)(PyObject *));
static struct LxmlNodeBase *((*rootNodeOrRaise)(PyObject *));
static PyObject *((*textOf)(xmlNode (*)));
static PyObject *((*tailOf)(xmlNode (*)));
static int ((*setNodeText)(xmlNode (*),PyObject *));
static int ((*setTailText)(xmlNode (*),PyObject *));
static PyObject *((*attributeValue)(xmlNode (*),xmlAttr (*)));
static PyObject *((*attributeValueFromNsName)(xmlNode (*),char (*),char (*)));
static PyObject *((*getAttributeValue)(struct LxmlNodeBase *,PyObject *,PyObject *));
static int ((*setAttributeValue)(struct LxmlNodeBase *,PyObject *,PyObject *));
static int ((*delAttribute)(struct LxmlNodeBase *,PyObject *));
static int ((*delAttributeFromNsName)(xmlNode (*),char (*),char (*)));
static xmlNode (*((*findChild)(xmlNode (*),Py_ssize_t )));
static xmlNode (*((*findChildForwards)(xmlNode (*),Py_ssize_t )));
static xmlNode (*((*findChildBackwards)(xmlNode (*),Py_ssize_t )));
static xmlNode (*((*nextElement)(xmlNode (*))));
static xmlNode (*((*previousElement)(xmlNode (*))));
static void ((*appendChild)(struct LxmlElement *,struct LxmlElement *));
static PyObject *((*pyunicode)(char (*)));
static PyObject *((*utf8)(PyObject *));
static PyObject *((*getNsTag)(PyObject *));
static PyObject *((*namespacedName)(xmlNode (*)));
static PyObject *((*namespacedNameFromNsName)(char (*),char (*)));
static void ((*iteratorStoreNext)(struct LxmlElementIterator *,struct LxmlNodeBase *));
static void ((*initTagMatch)(struct LxmlElementTagMatcher *,PyObject *));
static xmlNs (*((*findOrBuildNodeNs)(struct LxmlDocument *,xmlNode (*),char (*))));
static struct {char *s; void **p;} _etree_API[] = {
  {"deepcopyNodeToDocument", &deepcopyNodeToDocument},
  {"elementTreeFactory", &elementTreeFactory},
  {"newElementTree", &newElementTree},
  {"elementFactory", &elementFactory},
  {"setElementClassLookupFunction", &setElementClassLookupFunction},
  {"lookupDefaultElementClass", &lookupDefaultElementClass},
  {"lookupNamespaceElementClass", &lookupNamespaceElementClass},
  {"callLookupFallback", &callLookupFallback},
  {"tagMatches", &tagMatches},
  {"documentOrRaise", &documentOrRaise},
  {"rootNodeOrRaise", &rootNodeOrRaise},
  {"textOf", &textOf},
  {"tailOf", &tailOf},
  {"setNodeText", &setNodeText},
  {"setTailText", &setTailText},
  {"attributeValue", &attributeValue},
  {"attributeValueFromNsName", &attributeValueFromNsName},
  {"getAttributeValue", &getAttributeValue},
  {"setAttributeValue", &setAttributeValue},
  {"delAttribute", &delAttribute},
  {"delAttributeFromNsName", &delAttributeFromNsName},
  {"findChild", &findChild},
  {"findChildForwards", &findChildForwards},
  {"findChildBackwards", &findChildBackwards},
  {"nextElement", &nextElement},
  {"previousElement", &previousElement},
  {"appendChild", &appendChild},
  {"pyunicode", &pyunicode},
  {"utf8", &utf8},
  {"getNsTag", &getNsTag},
  {"namespacedName", &namespacedName},
  {"namespacedNameFromNsName", &namespacedNameFromNsName},
  {"iteratorStoreNext", &iteratorStoreNext},
  {"initTagMatch", &initTagMatch},
  {"findOrBuildNodeNs", &findOrBuildNodeNs},
  {0, 0}
};

/* Return -1 and set exception on error, 0 on success. */
static int
import_etree(PyObject *module)
{
    if (module != NULL) {
        PyObject *c_api_init = PyObject_GetAttrString(
                                   module, "_import_c_api");
        if (!c_api_init)
            return -1;
        if (PyCObject_Check(c_api_init))
        {
            int (*init)(struct {const char *s; const void **p;}*) =
                PyCObject_AsVoidPtr(c_api_init);
            if (!init) {
                PyErr_SetString(PyExc_RuntimeError,
                    "module returns NULL pointer for C API call");
                return -1;
            }
            init(_etree_API);
        }
        Py_DECREF(c_api_init);
    }
    return 0;
}
PyMODINIT_FUNC initetree(void);
#endif /* __HAS_PYX_etree */
