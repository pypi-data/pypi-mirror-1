#ifndef DOMLETTE_CHARACTERDATA_H
#define DOMLETTE_CHARACTERDATA_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "node.h"

  typedef struct {
    PyNode_HEAD
    PyObject *nodeValue;
  } PyCharacterDataObject;

#define PyCharacterData_NODE_VALUE(op) (((PyCharacterDataObject *)(op))->nodeValue)

  extern PyTypeObject DomletteCharacterData_Type;

#define PyCharacterData_Check(op) PyObject_TypeCheck((op), &DomletteCharacterData_Type)

  /* Module Methods */
  int DomletteCharacterData_Init(PyObject *module);
  void DomletteCharacterData_Fini(void);

  /* CharacterData Methods */
  extern PyObject *CharacterData_SubstringData(PyCharacterDataObject *node, 
                                               int offset, int count);
  extern int CharacterData_AppendData(PyCharacterDataObject *node, 
                                      PyObject *arg);
  extern int CharacterData_InsertData(PyCharacterDataObject *node, 
                                      int offset, PyObject *arg);
  extern int CharacterData_DeleteData(PyCharacterDataObject *node, 
                                      int offset, int count);
  extern int CharacterData_ReplaceData(PyCharacterDataObject *node, 
                                       int offset, int count, PyObject *arg);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_CHARACTERDATA_H */
