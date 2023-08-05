#ifndef DOMLETTE_DOCUMENT_H
#define DOMLETTE_DOCUMENT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "node.h"
#include "element.h"
#include "text.h"
#include "processinginstruction.h"
#include "comment.h"
#include "attr.h"
#include "documentfragment.h"

  typedef struct {
    PyContainerNode_HEAD
    PyObject *documentURI;
    PyObject *publicId;
    PyObject *systemId;
    PyObject *unparsedEntities;
    PyObject *creationIndex;
  } PyDocumentObject;

#define PyDocument_BASE_URI(op) (((PyDocumentObject *)(op))->documentURI)
#define PyDocument_PUBLIC_ID(op) (((PyDocumentObject *)(op))->publicId)
#define PyDocument_SYSTEM_ID(op) (((PyDocumentObject *)(op))->systemId)
#define PyDocument_INDEX(op) (((PyDocumentObject *)(op))->creationIndex)

  extern PyTypeObject DomletteDocument_Type;

#define PyDocument_Check(op) ((op)->ob_type == &DomletteDocument_Type)

  /* Module Methods */
  int DomletteDocument_Init(PyObject *module);
  void DomletteDocument_Fini(void);

  /* Document Methods */
  PyDocumentObject *Document_New(PyObject *documentURI);

  PyElementObject *Document_CreateElementNS(PyDocumentObject *self,
					    PyObject *namespaceURI,
                                            PyObject *qualifiedName,
					    PyObject *localName);


  PyAttrObject *Document_CreateAttributeNS(PyDocumentObject *self,
					   PyObject *namespaceURI,
                                           PyObject *qualifiedName,
					   PyObject *localName,
                                           PyObject *value);

  PyTextObject *Document_CreateTextNode(PyDocumentObject *ownerDoc,
					PyObject *data);

  PyProcessingInstructionObject *
  Document_CreateProcessingInstruction(PyDocumentObject *self,
				       PyObject *target, PyObject *data);

  PyCommentObject *Document_CreateComment(PyDocumentObject *self,
                                          PyObject *data);

  PyDocumentFragmentObject *
  Document_CreateDocumentFragment(PyDocumentObject *ownerDoc);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_DOCUMENT_H */
