#ifndef DOMLETTE_NODE_H
#define DOMLETTE_NODE_H

#ifdef __cplusplus
extern "C" {
#endif

#include "Python.h"
#include "nodetype.h"

  typedef struct _nodeobject PyNodeObject;

  /* PyNode_HEAD defines the initial segment of every Domlette node. */
#define PyNode_HEAD              \
    PyObject_HEAD                \
    long flags;                  \
    PyNodeObject *parentNode;    \
    PyObject *ownerDocument;

#define PyContainerNode_HEAD   \
    PyNode_HEAD                \
    int count;                 \
    PyNodeObject **nodes;      \
    int allocated;

  /* Nothing is actually declared to be a PyNodeObject, but every pointer to
   * a Domlette object can be cast to a PyNodeObject*.  This is inheritance
   * built by hand.
   */
  struct _nodeobject {
    PyNode_HEAD
  };

  typedef struct {
    PyContainerNode_HEAD
  } PyContainerNodeObject;

#define PyNode_OWNER_DOCUMENT(op) (((PyNodeObject *)(op))->ownerDocument)

#define Node_GET_PARENT(op) (((PyNodeObject *)(op))->parentNode)
#define Node_SET_PARENT(op, v) (Node_GET_PARENT(op) = (v))
#define Node_GET_DOCUMENT(op) (((PyNodeObject *)(op))->ownerDocument)

#define ContainerNode_GET_COUNT(op) (((PyContainerNodeObject *)(op))->count)
#define ContainerNode_GET_CHILD(op, i)          \
  (((PyContainerNodeObject *)(op))->nodes[i])

  extern PyTypeObject DomletteNode_Type;

#define PyNode_Check(op) PyObject_TypeCheck((op), &DomletteNode_Type)

  /* Module Methods */
  int DomletteNode_Init(PyObject *module);
  void DomletteNode_Fini(void);

  extern long g_nodeCount;

  /* PyNodeObject Creatation */
#define Node_FLAGS_CONTAINER (1L<<0)
#define Node_FLAGS_SHARED_ATTRIBUTES (1L<<1)

#define Node_HasFlag(n,f) ((n)->flags & (f))
#define Node_SetFlag(n,f) ((n)->flags |= (f))
#define Node_ClearFlag(n,f) ((n)->flags &= ~(f))

  PyNodeObject *_Node_New(PyTypeObject *type, PyObject *ownerDocument,
                          long flags);
#define Node_New(type, typeobj, ownerdoc) \
  ((type *) _Node_New((typeobj), (PyObject *)(ownerdoc), 0))
#define Node_NewContainer(type, typeobj, ownerdoc) \
  ((type *) _Node_New((typeobj), (PyObject *)(ownerdoc), Node_FLAGS_CONTAINER))
  
  void _Node_Del(PyNodeObject *node);
#define Node_Del(obj) _Node_Del((PyNodeObject *)(obj))

  int _Node_SetChildren(PyNodeObject *self, PyNodeObject **children, int size);

  /* DOM Node Methods */
  int Node_RemoveChild(PyNodeObject *self, PyNodeObject *oldChild);
  int Node_AppendChild(PyNodeObject *self, PyNodeObject *newChild);
  int Node_InsertBefore(PyNodeObject *self, PyNodeObject *newChild,
                        PyNodeObject *refChild);
  PyNodeObject *Node_CloneNode(PyObject *node, int deep,
			       PyNodeObject *newOwnerDocument);

#ifdef __cplusplus
}
#endif

#endif /* DOMLETTE_NODE_H */
