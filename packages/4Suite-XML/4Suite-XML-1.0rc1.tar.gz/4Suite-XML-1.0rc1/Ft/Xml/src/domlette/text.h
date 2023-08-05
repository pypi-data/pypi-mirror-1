#ifndef DOMLETTE_TEXT_H
#define DOMLETTE_TEXT_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "characterdata.h"

  typedef PyCharacterDataObject PyTextObject;

  extern PyTypeObject DomletteText_Type;

#define PyText_Check(op) ((op)->ob_type == &DomletteText_Type)
#define Text_GET_DATA(op) PyCharacterData_NODE_VALUE(op)
#define Text_SET_DATA(op, v) (Text_GET_DATA(op) = (v))

  /* Module Methods */
  int DomletteText_Init(PyObject *module);
  void DomletteText_Fini(void);

  /* Text Methods */
  PyTextObject *Text_CloneNode(PyObject *node, int deep,
			       PyNodeObject *newOwnerDocument);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_TEXT_H */
