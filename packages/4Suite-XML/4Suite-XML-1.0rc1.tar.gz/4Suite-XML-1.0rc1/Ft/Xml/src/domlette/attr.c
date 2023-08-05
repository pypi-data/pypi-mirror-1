#include "domlette.h"


/** Private Routines **************************************************/


#define Attr_VerifyState(ob)                          \
  if (!PyAttr_Check(ob) ||                            \
      ((PyAttrObject *)(ob))->nodeValue == NULL ||    \
      ((PyAttrObject *)(ob))->namespaceURI == NULL || \
      ((PyAttrObject *)(ob))->localName == NULL ||    \
      ((PyAttrObject *)(ob))->nodeName == NULL)       \
     return DOMException_InvalidStateErr("Attr in inconsistent state");


/** Public C API ******************************************************/


PyAttrObject *Attr_CloneNode(PyObject *node, int deep,
                             PyNodeObject *newOwnerDocument)
{
  PyObject *namespaceURI, *qualifiedName, *localName, *value;
  PyAttrObject *attr;
  
  namespaceURI = PyObject_GetAttrString(node, "namespaceURI");
  namespaceURI = DOMString_FromObjectInplace(namespaceURI);
  qualifiedName = PyObject_GetAttrString(node, "nodeName");
  qualifiedName = DOMString_FromObjectInplace(qualifiedName);
  localName = PyObject_GetAttrString(node, "localName");
  localName = DOMString_FromObjectInplace(localName);
  value = PyObject_GetAttrString(node, "value");
  value = DOMString_FromObjectInplace(value);
  if (namespaceURI == NULL || qualifiedName == NULL || localName == NULL ||
      value == NULL) {
    Py_XDECREF(value);
    Py_XDECREF(localName);
    Py_XDECREF(qualifiedName);
    Py_XDECREF(namespaceURI);
    return NULL;
  }

  attr = Document_CreateAttributeNS((PyDocumentObject*) newOwnerDocument,
                                    namespaceURI, qualifiedName, localName,
                                    value);
  Py_DECREF(value);
  Py_DECREF(localName);
  Py_DECREF(qualifiedName);
  Py_DECREF(namespaceURI);
  return attr;
}


/** Python Methods ****************************************************/


/* No additional interface methods defined */


/** Python Members ****************************************************/


static struct PyMemberDef attr_members[] = {
  { "name",         T_OBJECT, offsetof(PyAttrObject, nodeName),     RO },
  { "nodeName",     T_OBJECT, offsetof(PyAttrObject, nodeName),     RO },
  { "namespaceURI", T_OBJECT, offsetof(PyAttrObject, namespaceURI), RO },
  { "localName",    T_OBJECT, offsetof(PyAttrObject, localName),    RO },
  { "ownerElement", T_OBJECT, offsetof(PyAttrObject, parentNode),   RO },
  { NULL }
};


/** Python Computed Members *******************************************/


static PyObject *get_prefix(PyAttrObject *self, void *arg)
{
  Py_UNICODE *p = PyUnicode_AS_UNICODE(self->nodeName);
  int i, len;

  len = PyUnicode_GET_SIZE(self->nodeName);
  for (i = 0; i < len; i++) {
    if (p[i] == ':') {
      return PyUnicode_FromUnicode(p, (Py_ssize_t)i);
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}


static int set_prefix(PyAttrObject *self, PyObject *v, void *arg)
{
  PyObject *qualifiedName, *prefix;
  Py_ssize_t size;

  prefix = DOMString_ConvertArgument(v, (char *)arg, 1);
  if (prefix == NULL) {
    return -1;
  } else if (prefix == Py_None) {
    Py_DECREF(self->nodeName);
    Py_INCREF(self->localName);
    self->nodeName = self->localName;
    return 0;
  }

  /* rebuild the qualifiedName */
  size = PyUnicode_GET_SIZE(prefix) + 1 + PyUnicode_GET_SIZE(self->localName);
  qualifiedName = PyUnicode_FromUnicode(NULL, size);
  if (qualifiedName == NULL) {
    Py_DECREF(prefix);
    return -1;
  }

  /* copy the prefix to the qualifiedName string */
  size = PyUnicode_GET_SIZE(prefix);
  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(qualifiedName), 
                  PyUnicode_AS_UNICODE(prefix), size);
  Py_DECREF(prefix);

  /* add the ':' separator */
  PyUnicode_AS_UNICODE(qualifiedName)[size++] = (Py_UNICODE) ':';

  /* add the localName after the ':' to finish the qualifiedName */
  Py_UNICODE_COPY(PyUnicode_AS_UNICODE(qualifiedName) + size,
                  PyUnicode_AS_UNICODE(self->localName),
                  PyUnicode_GET_SIZE(self->localName));

  Py_DECREF(self->nodeName);
  self->nodeName = qualifiedName;
  return 0;
}


static PyObject *get_value(PyAttrObject *self, void *arg)
{
  Py_INCREF(self->nodeValue);
  return self->nodeValue;
}


static int set_value(PyAttrObject *self, PyObject *v, void *arg)
{
  PyObject *nodeValue = DOMString_ConvertArgument(v, (char *)arg, 0);
  if (nodeValue == NULL) return -1;

  Py_DECREF(self->nodeValue);
  self->nodeValue = nodeValue;
  return 0;
}


static struct PyGetSetDef attr_getset[] = {
  { "prefix",    (getter)get_prefix, (setter)set_prefix, NULL, "prefix" },
  { "value",     (getter)get_value,  (setter)set_value,  NULL, "value" },
  { "nodeValue", (getter)get_value,  (setter)set_value,  NULL, "nodeValue" },
  { NULL }
};


/** Type Object ********************************************************/


static void attr_dealloc(PyAttrObject *node)
{

  PyObject_GC_UnTrack((PyObject *) node);

  Py_XDECREF(node->namespaceURI);
  node->namespaceURI = NULL;

  Py_XDECREF(node->localName);
  node->localName = NULL;

  Py_XDECREF(node->nodeName);
  node->nodeName = NULL;

  Py_XDECREF(node->nodeValue);
  node->nodeValue = NULL;

  Node_Del(node);
}


static PyObject *attr_repr(PyAttrObject *attr)
{
  PyObject *repr;
  PyObject *name = PyObject_Repr(attr->nodeName);
  PyObject *value = PyObject_Repr(attr->nodeValue);
  if (name == NULL || value == NULL) {
    Py_XDECREF(name);
    Py_XDECREF(value);
    return NULL;
  }
  repr = PyString_FromFormat("<Attr at %p: name %s, value %s>", attr,
                             PyString_AS_STRING(name), 
                             PyString_AS_STRING(value));
  Py_DECREF(name);
  Py_DECREF(value);
  return repr;
}


static char attr_doc[] = 
"The Attr interface represents an attribute in an Element object.";

PyTypeObject DomletteAttr_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ DOMLETTE_PACKAGE "Attr",
  /* tp_basicsize      */ sizeof(PyAttrObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) attr_dealloc,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) attr_repr,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) 0,
  /* tp_as_mapping     */ (PyMappingMethods *) 0,
  /* tp_hash           */ (hashfunc) 0,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ Py_TPFLAGS_DEFAULT,
  /* tp_doc            */ (char *) attr_doc,
  /* tp_traverse       */ (traverseproc) 0,
  /* tp_clear          */ (lenfunc) 0,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) 0,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) 0,
  /* tp_members        */ (PyMemberDef *) attr_members,
  /* tp_getset         */ (PyGetSetDef *) attr_getset,
  /* tp_base           */ (PyTypeObject *) 0,
  /* tp_dict           */ (PyObject *) 0,
  /* tp_descr_get      */ (descrgetfunc) 0,
  /* tp_descr_set      */ (descrsetfunc) 0,
  /* tp_dictoffset     */ 0,
  /* tp_init           */ (initproc) 0,
  /* tp_alloc          */ (allocfunc) 0,
  /* tp_new            */ (newfunc) 0,
  /* tp_free           */ 0,
};


/** Module Setup & Teardown *******************************************/


int DomletteAttr_Init(PyObject *module)
{
  PyObject *dict, *value;

  DomletteAttr_Type.tp_base = &DomletteNode_Type;
  if (PyType_Ready(&DomletteAttr_Type) < 0)
    return -1;

  dict = DomletteAttr_Type.tp_dict;

  value = PyInt_FromLong(ATTRIBUTE_NODE);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(dict, "nodeType", value))
    return -1;
  Py_DECREF(value);

  /* Override default behavior from Node */
  if (PyDict_SetItemString(dict, "previousSibling", Py_None))
    return -1;

  /* Override default behavior from Node */
  if (PyDict_SetItemString(dict, "nextSibling", Py_None))
    return -1;

  /* Until the DTD information is used, assume it was from the document */
  value = PyInt_FromLong(1);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(dict, "specified", value))
    return -1;
  Py_DECREF(value);

  Py_INCREF(&DomletteAttr_Type);
  return PyModule_AddObject(module, "Attr", (PyObject*) &DomletteAttr_Type);
}


void DomletteAttr_Fini(void)
{
  PyType_CLEAR(&DomletteAttr_Type);
}
