#ifndef COMMON_H
#define COMMON_H

/* Backward compat code recommended in PEP 353 */
#if PY_VERSION_HEX < 0x02050000
    typedef int Py_ssize_t;
#   define PY_SSIZE_T_MAX INT_MAX
#   define PY_SSIZE_T_MIN INT_MIN
#   define ssizeargfunc intargfunc
#   define ssizessizeargfunc intintargfunc
#   define ssizeobjargproc intobjargproc
#   define ssizessizeobjargproc intintobjargproc
#   define lenfunc inquiry
#endif

/*
#if !defined(Py_ssize_t)
#  define Py_ssize_t int
#endif
*/

#endif /* COMMON_H */

