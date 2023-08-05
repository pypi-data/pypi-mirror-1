#ifndef DOMLETTE_COMMENT_H
#define DOMLETTE_COMMENT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "characterdata.h"

  typedef PyCharacterDataObject PyCommentObject;

  extern PyTypeObject DomletteComment_Type;

#define PyComment_Check(op) ((op)->ob_type == &DomletteComment_Type)

  /* Module Methods */
  int DomletteComment_Init(PyObject *module);
  void DomletteComment_Fini(void);

  /* Comment Methods */
  PyCommentObject *Comment_CloneNode(PyObject *comment, int deep,
				     PyNodeObject *newOwnerDocument);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_COMMENT_H */
