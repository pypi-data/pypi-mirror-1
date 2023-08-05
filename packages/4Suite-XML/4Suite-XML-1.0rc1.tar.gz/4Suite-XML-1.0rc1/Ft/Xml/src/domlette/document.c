#include "domlette.h"
#include "xmlstring.h"

static PyObject *creation_counter, *counter_inc;
static PyObject *shared_empty_attributes;

/** Private Routines **************************************************/


/* returns borrowed reference */
static PyObject *get_element_by_id(PyNodeObject *node, PyObject *elementId)
{
  int i;

  for (i = 0; i < ContainerNode_GET_COUNT(node); i++) {
    PyNodeObject *child = ContainerNode_GET_CHILD(node, i);
    if (PyElement_Check(child)) {
      PyObject *tmp, *attr;
      Py_ssize_t pos = 0;
      /* Searth the attributes for an ID attr */
      while (PyDict_Next(PyElement_ATTRIBUTES(child), &pos, &tmp, &attr)) {
        if (Attr_GET_TYPE(attr) == ATTRIBUTE_TYPE_ID) {
          tmp = PyAttr_NODE_VALUE(attr);
          switch (PyObject_RichCompareBool(tmp, elementId, Py_EQ)) {
          case 1:
            /* Found matching element, return it. */
            return (PyObject *) child;
          case 0:
            break;
          default:
            return NULL;
          }
        }
      }
      /* Continue on with the children */
      tmp = get_element_by_id(child, elementId);
      /* either NULL (an error) or a node (element found) */
      if (tmp != Py_None) return tmp;
    }
  }
  return Py_None;
}


/** Public C API ******************************************************/


PyDocumentObject *Document_New(PyObject *documentURI)
{
  PyDocumentObject *self;

  self = Node_NewContainer(PyDocumentObject, &DomletteDocument_Type, Py_None);
  if (self == NULL)
    return NULL;

  /* assign members */
  self->creationIndex = PyNumber_Add(creation_counter, counter_inc);
  if (self->creationIndex == NULL) {
    Node_Del(self);
    return NULL;
  } else {
    /* update creation counter */
    Py_DECREF(creation_counter);
    creation_counter = self->creationIndex;
    Py_INCREF(creation_counter);
  }

  self->unparsedEntities = PyDict_New();
  if (self->unparsedEntities == NULL) {
    Py_DECREF(self->creationIndex);
    Node_Del(self);
    return NULL;
  }

  if (documentURI == Py_None) {
    documentURI = PyUnicode_FromUnicode(NULL, (Py_ssize_t)0);
    if (documentURI == NULL) {
      Py_DECREF(self->unparsedEntities);
      Py_DECREF(self->creationIndex);
      Node_Del(self);
      return NULL;
    }
  } else {
    Py_INCREF(documentURI);
  }
  self->documentURI = documentURI;

  self->publicId = Py_None;
  Py_INCREF(Py_None);

  self->systemId = Py_None;
  Py_INCREF(Py_None);

  PyObject_GC_Track(self);

  return self;
}


PyElementObject *Document_CreateElementNS(PyDocumentObject *doc,
					  PyObject *namespaceURI,
                                          PyObject *qualifiedName,
					  PyObject *localName)
{
  PyElementObject *element;

  if (!(PyDocument_Check(doc) &&
        (DOMString_Check(namespaceURI) || namespaceURI == Py_None) &&
        DOMString_Check(qualifiedName) &&
        DOMString_Check(localName))) {
    PyErr_BadInternalCall();
    return NULL;
  }

  element = Node_NewContainer(PyElementObject, &DomletteElement_Type, doc);
  if (!element)
    return NULL;

  Py_INCREF(namespaceURI);
  element->namespaceURI = namespaceURI;

  Py_INCREF(localName);
  element->localName = localName;

  Py_INCREF(qualifiedName);
  element->nodeName = qualifiedName;

  Node_SetFlag(element, Node_FLAGS_SHARED_ATTRIBUTES);
  Py_INCREF(shared_empty_attributes);
  element->attributes = shared_empty_attributes;

  PyObject_GC_Track(element);

  return element;
}


PyAttrObject *Document_CreateAttributeNS(PyDocumentObject *doc,
					 PyObject *namespaceURI,
                                         PyObject *qualifiedName,
					 PyObject *localName,
                                         PyObject *value)
{
  PyAttrObject *attr;

  if (!(PyDocument_Check(doc) &&
        (DOMString_Check(namespaceURI) || namespaceURI == Py_None) &&
        DOMString_Check(qualifiedName) &&
        DOMString_Check(localName) &&
        (value == NULL || DOMString_Check(value)))) {
    PyErr_BadInternalCall();
    return NULL;
  }

  attr = Node_New(PyAttrObject, &DomletteAttr_Type, doc);
  if (attr == NULL)
    return NULL;

  if (value == NULL) {
    value = PyUnicode_FromUnicode(NULL, (Py_ssize_t)0);
    if (value == NULL) {
      Node_Del(attr);
      return NULL;
    }
  } else {
    Py_INCREF(value);
  }

  Py_INCREF(namespaceURI);
  attr->namespaceURI = namespaceURI;

  Py_INCREF(localName);
  attr->localName = localName;

  Py_INCREF(qualifiedName);
  attr->nodeName = qualifiedName;

  attr->nodeValue = value;

  attr->type = ATTRIBUTE_TYPE_CDATA;

  PyObject_GC_Track(attr);

  return attr;
}


PyTextObject *Document_CreateTextNode(PyDocumentObject *doc, PyObject *data)
{
  PyTextObject *text;

  if (!(PyDocument_Check(doc) && DOMString_Check(data))) {
    PyErr_BadInternalCall();
    return NULL;
  }

  text = Node_New(PyTextObject, &DomletteText_Type, doc);
  if (text == NULL)
    return NULL;

  Py_INCREF(data);
  text->nodeValue = data;

  PyObject_GC_Track(text);

  return text;
}


PyCommentObject *Document_CreateComment(PyDocumentObject *doc, PyObject *data)
{
  PyCommentObject *comment;

  if (!(PyDocument_Check(doc) && DOMString_Check(data))) {
    PyErr_BadInternalCall();
    return NULL;
  }

  comment = Node_New(PyCommentObject, &DomletteComment_Type, doc);
  if (comment == NULL)
    return NULL;

  Py_INCREF(data);
  comment->nodeValue = data;

  PyObject_GC_Track(comment);

  return comment;
}


PyProcessingInstructionObject *Document_CreateProcessingInstruction(
                                    PyDocumentObject *doc,
                                    PyObject *target,
                                    PyObject *data)
{
  PyProcessingInstructionObject *pi;

  if (!(PyDocument_Check(doc) && 
        DOMString_Check(target) && 
        DOMString_Check(data))) {
    PyErr_BadInternalCall();
    return NULL;
  }

  pi = Node_New(PyProcessingInstructionObject,
		&DomletteProcessingInstruction_Type, doc);
  if (pi == NULL)
    return NULL;

  Py_INCREF(target);
  pi->nodeName = target;

  Py_INCREF(data);
  pi->nodeValue = data;

  PyObject_GC_Track(pi);

  return pi;
}


PyDocumentFragmentObject *
Document_CreateDocumentFragment(PyDocumentObject *doc)
{
  /*Returns new reference*/
  PyDocumentFragmentObject *df;

  if (!PyDocument_Check(doc)) {
    PyErr_BadInternalCall();
    return NULL;
  }

  df = Node_NewContainer(PyDocumentFragmentObject, 
                         &DomletteDocumentFragment_Type, doc);
  if (df == NULL)
    return NULL;

  PyObject_GC_Track(df);

  return df;
}


/** Python Methods ****************************************************/


static char document_createElementNS_doc[] =
"createElementNS(namespaceURI, qualifiedName) -> new Element\n\
\n\
Creates an element of the given qualified name and namespace URI.";

static PyObject *document_createElementNS(PyObject *self, PyObject *args)
{
  PyObject *res;
  PyObject *namespaceURI, *qualifiedName, *localName, *prefix;

  if(!PyArg_ParseTuple(args, "OO:createElementNS",
		       &namespaceURI, &qualifiedName))
    return NULL;

  namespaceURI = DOMString_ConvertArgument(namespaceURI, "namespaceURI", 1);
  if (namespaceURI == NULL) return NULL;

  qualifiedName = DOMString_ConvertArgument(qualifiedName, "qualifiedName", 0);
  if (qualifiedName == NULL) {
    Py_DECREF(namespaceURI);
    return NULL;
  }

  if (!XmlString_SplitQName(qualifiedName, &prefix, &localName)) {
    Py_DECREF(namespaceURI);
    Py_DECREF(qualifiedName);
    return NULL;
  }

  if (namespaceURI == Py_None && prefix != Py_None) {
    DOMException_NamespaceErr("prefix requires non-null namespaceURI");
    Py_DECREF(namespaceURI);
    Py_DECREF(prefix);
    return NULL;
  }
  Py_DECREF(prefix);

  res = (PyObject *)Document_CreateElementNS((PyDocumentObject *)self,
                                             namespaceURI, qualifiedName, 
                                             localName);
  Py_DECREF(namespaceURI);
  Py_DECREF(qualifiedName);
  Py_DECREF(localName);
  return res;
}


static char document_createAttributeNS_doc[] =
"createAttributeNS(namespaceURI, qualifiedName) -> new Attribute\n\
\n\
Creates an attribute of the given qualified name and namespace URI.";

static PyObject *document_createAttributeNS(PyObject *self, PyObject *args)
{
  PyObject *res;
  PyObject *namespaceURI, *qualifiedName, *localName, *prefix;

  if (!PyArg_ParseTuple(args, "OO:createAttributeNS",
			&namespaceURI, &qualifiedName))
    return NULL;

  namespaceURI = DOMString_ConvertArgument(namespaceURI, "namespaceURI", 1);
  if (namespaceURI == NULL) return NULL;

  qualifiedName = DOMString_ConvertArgument(qualifiedName, "qualifiedName", 0);
  if (qualifiedName == NULL) {
    Py_DECREF(namespaceURI);
    return NULL;
  }

  if (!XmlString_SplitQName(qualifiedName, &prefix, &localName)) {
    Py_DECREF(namespaceURI);
    Py_DECREF(qualifiedName);
    return NULL;
  }

  if (namespaceURI == Py_None && prefix != Py_None) {
    DOMException_NamespaceErr("prefix requires non-null namespaceURI");
    Py_DECREF(namespaceURI);
    Py_DECREF(prefix);
    return NULL;
  }
  Py_DECREF(prefix);

  res = (PyObject *)Document_CreateAttributeNS((PyDocumentObject *)self,
                                               namespaceURI, qualifiedName, 
                                               localName, NULL);

  Py_DECREF(namespaceURI);
  Py_DECREF(qualifiedName);
  Py_DECREF(localName);
  return res;
}


static char document_createTextNode_doc[] =
"createTextNode(data) -> new Text\n\
\n\
Creates a Text node given the specified string.";

static PyObject *document_createTextNode(PyObject *self, PyObject *args)
{
  PyObject *res;
  PyObject *data;

  if(!PyArg_ParseTuple(args, "O:createTextNode", &data))
    return NULL;

  data = DOMString_ConvertArgument(data, "data", 0);
  if (data == NULL) return NULL;

  res = (PyObject *)Document_CreateTextNode((PyDocumentObject *)self, data);
  Py_DECREF(data);
  return res;
}


static char document_createProcessingInstruction_doc[] =
"createProcessingInstruction(target, data) -> new ProcessingInstruction\n\
\n\
Creates a ProcessingInstruction node given the specified name and data\n\
strings.";

static PyObject *document_createProcessingInstruction(PyObject *self,
                                                      PyObject *args)
{
  PyProcessingInstructionObject *pi;
  PyObject *target, *data;

  if (!PyArg_ParseTuple(args,"OO:createProcessingInstruction", &target, &data))
    return NULL;

  target = DOMString_ConvertArgument(target, "target", 0);
  if (target == NULL) return NULL;

  data = DOMString_ConvertArgument(data, "data", 0);
  if (data == NULL) {
    Py_DECREF(target);
    return NULL;
  }

  pi = Document_CreateProcessingInstruction((PyDocumentObject *)self, target,
					    data);
  Py_DECREF(data);
  Py_DECREF(target);
  return (PyObject *)pi;
}


static char document_createComment_doc[] =
"createComment(data) -> new Comment\n\
\n\
Creates a Comment node given the specified string.";

static PyObject *document_createComment(PyObject *self, PyObject *args)
{
  PyCommentObject *comment;
  PyObject *data;

  if (!PyArg_ParseTuple(args, "O:createComment", &data))
    return NULL;

  data = DOMString_ConvertArgument(data, "data", 0);
  if (data == NULL) return NULL;

  comment = Document_CreateComment((PyDocumentObject *)self, data);

  Py_DECREF(data);
  return (PyObject *)comment;
}

static char document_createDocumentFragment_doc[] =
"createDocumentFragment() -> new DocumentFragment\n\
\n\
Creates an empty DocumentFragment object.";

static PyObject *document_createDocumentFragment(PyObject *self,
                                                 PyObject *args)
{
  if (!PyArg_ParseTuple(args, ":createDocumentFragment"))
    return NULL;

  return (PyObject *)Document_CreateDocumentFragment((PyDocumentObject *)self);
}

static char document_importNode_doc[] =
"importNode(importedNode, deep) -> Node\n\
\n\
Imports a node from another document to this document. The returned node\n\
has no parent; (parentNode is None). The source node is not altered or\n\
removed from the original document; this method creates a new copy of the\n\
source node.";

static PyObject *document_importNode(PyObject *self, PyObject *args)
{
  PyObject *node, *boolean_deep = Py_False;
  int deep;
    
  if (!PyArg_ParseTuple(args,"O|O:importNode", &node, &boolean_deep))
    return NULL;

  deep = PyObject_IsTrue(boolean_deep);
  if (deep == -1)
    return NULL;

  return (PyObject *)Node_CloneNode(node, deep, (PyNodeObject *)self);
}


static char document_getElementById_doc[] =
"getElementById(elementId) -> Element\n\
\n\
Returns the Element whose ID is given by elementId. If no such element\n\
exists, returns None. If more than one element has this ID, the first in\n\
the document is returned.";

static PyObject *document_getElementById(PyObject *self, PyObject *args)
{
  PyObject *elementId, *element;
  int i;

  if (!PyArg_ParseTuple(args, "O:getElementById", &elementId))
    return NULL;

  /* our "document" can have multiple element children */
  for (i = 0; i < ContainerNode_GET_COUNT(self); i++) {
    PyNodeObject *node = ContainerNode_GET_CHILD(self, i);
    if (PyElement_Check(node)) {
      element = get_element_by_id(node, elementId);
      if (element == NULL) return NULL;
      else if (element != Py_None) {
        Py_INCREF(element);
        return element;
      }
    }
  }

  Py_INCREF(Py_None);
  return Py_None;
}


#define document_method(NAME) \
  { #NAME, document_##NAME, METH_VARARGS, document_##NAME##_doc }

static struct PyMethodDef document_methods[] = {
  document_method(createElementNS),
  document_method(createAttributeNS),
  document_method(createTextNode),
  document_method(createProcessingInstruction),
  document_method(createComment),
  document_method(createDocumentFragment),
  document_method(importNode),
  document_method(getElementById),
  { NULL }
};


/** Python Members ****************************************************/


#define Document_MEMBER(name, member) \
  { name, T_OBJECT, offsetof(PyDocumentObject, member), RO }

static struct PyMemberDef document_members[] = {
  Document_MEMBER("unparsedEntities", unparsedEntities),
  /* deprecated */
  Document_MEMBER("refUri", documentURI),
  Document_MEMBER("xmlBase", documentURI),
  { NULL }
};


/** Python Computed Members *******************************************/


static PyObject *get_root_node(PyDocumentObject *self, void *arg)
{
  Py_INCREF(self);
  return (PyObject *)self;
}


static PyObject *get_document_element(PyDocumentObject *self, void *arg)
{
  int i;
  for (i = 0; i < ContainerNode_GET_COUNT(self); i++) {
    PyNodeObject *child = ContainerNode_GET_CHILD(self, i);
    if (PyElement_Check(child)) {
      Py_INCREF(child);
      return (PyObject *) child;
    }
  }
  Py_INCREF(Py_None);
  return Py_None;
}


static PyObject *get_document_uri(PyDocumentObject *self, void *arg)
{
  Py_INCREF(self->documentURI);
  return self->documentURI;
}


static int set_document_uri(PyDocumentObject *self, PyObject *v, void *arg)
{
  if ((v = DOMString_ConvertArgument(v, "documentURI", 1)) == NULL) 
    return -1;
  Py_DECREF(self->documentURI);
  self->documentURI = v;
  return 0;
}


static PyObject *get_public_id(PyDocumentObject *self, void *arg)
{
  Py_INCREF(self->publicId);
  return self->publicId;
}


static int set_public_id(PyDocumentObject *self, PyObject *v, void *arg)
{
  if ((v = DOMString_ConvertArgument(v, "publicId", 1)) == NULL) 
    return -1;
  Py_DECREF(self->publicId);
  self->publicId = v;
  return 0;
}


static PyObject *get_system_id(PyDocumentObject *self, void *arg)
{
  Py_INCREF(self->systemId);
  return self->systemId;
}


static int set_system_id(PyDocumentObject *self, PyObject *v, void *arg)
{
  if ((v = DOMString_ConvertArgument(v, "systemId", 1)) == NULL) 
    return -1;
  Py_DECREF(self->systemId);
  self->systemId = v;
  return 0;
}


static struct PyGetSetDef document_getset[] = {
  { "rootNode",        (getter)get_root_node },
  { "documentElement", (getter)get_document_element },
  { "documentURI",     (getter)get_document_uri, (setter)set_document_uri },
  { "publicId",        (getter)get_public_id,    (setter)set_public_id },
  { "systemId",        (getter)get_system_id,    (setter)set_system_id },
  { NULL }
};


/** Type Object ********************************************************/


static void document_dealloc(PyDocumentObject *self)
{
  PyObject_GC_UnTrack((PyObject *) self);

  Py_XDECREF(self->documentURI);
  self->documentURI = NULL;

  Py_XDECREF(self->unparsedEntities);
  self->unparsedEntities = NULL;

  Py_XDECREF(self->creationIndex);
  self->creationIndex = NULL;

  Node_Del(self);
}


static PyObject *document_repr(PyDocumentObject *document)
{
  return PyString_FromFormat("<Document at %p: %d children>", document,
                             ContainerNode_GET_COUNT(document));
}


static int document_traverse(PyDocumentObject *self, visitproc visit,
                             void *arg)
{
  Py_VISIT(self->unparsedEntities);
  PyType_TRAVERSE_BASE((PyObject *) self);
  return 0;
}


static int document_clear(PyDocumentObject *self)
{
  Py_CLEAR(self->unparsedEntities);
  PyType_CLEAR_BASE((PyObject *) self);
  return 0;
}


static char document_doc[] =
"The Document interface represents the entire XML document. Conceptually,\n\
it is the root of the document tree, and provides the primary access to the\n\
document's data.";


PyTypeObject DomletteDocument_Type = {
  /* PyObject_HEAD     */ PyObject_HEAD_INIT(NULL)
  /* ob_size           */ 0,
  /* tp_name           */ DOMLETTE_PACKAGE "Document",
  /* tp_basicsize      */ sizeof(PyDocumentObject),
  /* tp_itemsize       */ 0,
  /* tp_dealloc        */ (destructor) document_dealloc,
  /* tp_print          */ (printfunc) 0,
  /* tp_getattr        */ (getattrfunc) 0,
  /* tp_setattr        */ (setattrfunc) 0,
  /* tp_compare        */ (cmpfunc) 0,
  /* tp_repr           */ (reprfunc) document_repr,
  /* tp_as_number      */ (PyNumberMethods *) 0,
  /* tp_as_sequence    */ (PySequenceMethods *) 0,
  /* tp_as_mapping     */ (PyMappingMethods *) 0,
  /* tp_hash           */ (hashfunc) 0,
  /* tp_call           */ (ternaryfunc) 0,
  /* tp_str            */ (reprfunc) 0,
  /* tp_getattro       */ (getattrofunc) 0,
  /* tp_setattro       */ (setattrofunc) 0,
  /* tp_as_buffer      */ (PyBufferProcs *) 0,
  /* tp_flags          */ Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_GC,
  /* tp_doc            */ (char *) document_doc,
  /* tp_traverse       */ (traverseproc) document_traverse,
  /* tp_clear          */ (lenfunc) document_clear,
  /* tp_richcompare    */ (richcmpfunc) 0,
  /* tp_weaklistoffset */ 0,
  /* tp_iter           */ (getiterfunc) 0,
  /* tp_iternext       */ (iternextfunc) 0,
  /* tp_methods        */ (PyMethodDef *) document_methods,
  /* tp_members        */ (PyMemberDef *) document_members,
  /* tp_getset         */ (PyGetSetDef *) document_getset,
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


int DomletteDocument_Init(PyObject *module)
{
  PyObject *dict, *value;

  XmlString_IMPORT;

  DomletteDocument_Type.tp_base = &DomletteNode_Type;
  if (PyType_Ready(&DomletteDocument_Type) < 0)
    return -1;

  dict = DomletteDocument_Type.tp_dict;

  value = PyInt_FromLong(DOCUMENT_NODE);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(dict, "nodeType", value))
    return -1;
  Py_DECREF(value);
  
  value = PyUnicode_DecodeASCII("#document", (Py_ssize_t)9, NULL);
  if (value == NULL)
    return -1;
  if (PyDict_SetItemString(dict, "nodeName", value))
    return -1;
  Py_DECREF(value);

  if (PyDict_SetItemString(dict, "ownerDocument", Py_None))
    return -1;

  if (PyDict_SetItemString(dict, "doctype", Py_None))
    return -1;

  if (PyDict_SetItemString(dict, "implementation", g_implementation))
    return -1;

  creation_counter = PyLong_FromLong(0L);
  if (creation_counter == NULL) return -1;

  counter_inc = PyLong_FromLong(1L);
  if (counter_inc == NULL) return -1;

  shared_empty_attributes = PyDict_New();
  if (shared_empty_attributes == NULL) return -1;

  Py_INCREF(&DomletteDocument_Type);
  return PyModule_AddObject(module, "Document",
                            (PyObject*) &DomletteDocument_Type);
}

void DomletteDocument_Fini(void)
{
  Py_DECREF(creation_counter);
  Py_DECREF(counter_inc);
  Py_DECREF(shared_empty_attributes);

  PyType_CLEAR(&DomletteDocument_Type);
}
