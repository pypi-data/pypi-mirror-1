#ifndef _ARRAY_INTERFACE_H_
#define _ARRAY_INTERFACE_H_

#include "Python.h"

#define __PY_ARRAY_INTERFACE_VERSION__ 0x0002

enum PyGenericArray_KINDS {
	PyArrayKind_BOOL='b',
	PyArrayKind_INT='i',
	PyArrayKind_UINT='u',
	PyArrayKind_FLOAT='f',
	PyArrayKind_COMPLEX='c',
	PyArrayKind_STRING='S',
	PyArrayKind_UNICODE='U',
	PyArrayKind_OBJECT='O',
	PyArrayKind_RECORD='R',
	PyArrayKind_VOID='V',
	PyArrayKind_BIT='t',
	PyArrayKind_OTHER='X'
};

#define GA_CONTIGUOUS	0x01
#define	GA_FORTRAN		0x02
#define	GA_ALIGNED		0x100
#define	GA_NOTSWAPPED	0x200
#define	GA_WRITEABLE	0x400

typedef struct  {
    int version;                     // always equals 2?
    int nd;                          // number of dimensions
    char typekind;                   // elements kind - PyDimArray_KINDS
    int itemsize;                    // size of each element
    int flags;                       // flags indicating how the data should be interpreted
    Py_intptr_t *shape;				 // A length-nd array of shape information
    Py_intptr_t *strides;			 // A length-nd array of stride information
    void *data;                      // A pointer to the first element of the array
} PyGenericArrayInterface;

#define GA_CONTINUOUS_C (GA_CONTIGUOUS | GA_ALIGNED | GA_WRITEABLE)
#define GA_CONTINUOUS_C_RO (GA_CONTIGUOUS | GA_ALIGNED)

#define PyArrayInterface_IS_KIND(ai, kind) ((ai->typekind) == kind)

#define PyArrayInterface_IS_C_ARRAY(ai)     (((ai->flags) & (GA_CONTIGUOUS | GA_ALIGNED | GA_WRITEABLE)) == GA_CONTINUOUS_C)
#define PyArrayInterface_IS_C_ARRAY_RO(ai)  (((ai->flags) & GA_CONTINUOUS_C_RO) == GA_CONTINUOUS_C_RO)

#define PyArrayInterface_IS_CONTIGUOUS(ai)	((ai->flags) & GA_CONTIGUOUS)
#define PyArrayInterface_IS_FORTRAN(ai)		((ai->flags) & GA_FORTRAN)
#define PyArrayInterface_IS_WRITABLE(ai)	((ai->flags) & GA_WRITABLE)
#define PyArrayInterface_IS_ALIGNED(ai)		((ai->flags) & GA_ALIGNED)

#define PyArrayInterface_VERSION(ai)		((ai)->version)
#define PyArrayInterface_ND(ai)				((ai)->nd)
#define PyArrayInterface_TYPEKIND(ai)		((ai)->typekind)
#define PyArrayInterface_ITEMSIZE(ai)		((ai)->itemsize)
#define PyArrayInterface_FLAGS(ai)			((ai)->flags)
#define PyArrayInterface_SHAPES(ai)			((ai)->shape)
#define PyArrayInterface_SHAPE(ai, n)		((ai)->shape[n])
#define PyArrayInterface_STRIDES(ai)		((ai)->strides)
#define PyArrayInterface_STRIDE(ai, n)		((ai)->stride[n])
#define PyArrayInterface_DATA(ai)			((ai)->data)

#define PyArrayInterface_DATA_AS_DOUBLE_C_ARRAY(ai)		((PyArrayInterface_IS_C_ARRAY(ai) && PyArrayInterface_IS_KIND(ai, PyArrayKind_FLOAT) && (PyArrayInterface_ITEMSIZE(ai) == 8))? ((double*)(ai)->data) : NULL )
#define PyArrayInterface_DATA_AS_DOUBLE_C_ARRAY_RO(ai)	((PyArrayInterface_IS_C_ARRAY_RO(ai) && PyArrayInterface_IS_KIND(ai, PyArrayKind_FLOAT) && (PyArrayInterface_ITEMSIZE(ai) == 8))? ((double*)(ai)->data) : NULL )

#define PyArrayInterface_CHECK(ai)		(ai->version == __PY_ARRAY_INTERFACE_VERSION__)
#define PyArrayInterface_CHECK_1D(ai)	(PyArrayInterface_CHECK(ai) && PyArrayInterface_ND(ai) == 1)
#define PyArrayInterface_CHECK_2D(ai)	(PyArrayInterface_CHECK(ai) && PyArrayInterface_ND(ai) == 2)

#endif
