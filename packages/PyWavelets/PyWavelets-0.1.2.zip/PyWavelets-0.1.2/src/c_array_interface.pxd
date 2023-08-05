# see http://numeric.scipy.org/array_interface.html
# see http://new.scipy.org/Wiki/Cookbook/ArrayStruct_and_Pyrex

cdef extern from "array_interface.h":

    ctypedef struct PyGenericArrayInterface:
        int version                     # contains the integer 2 as a sanity check
        int nd                          # number of dimensions
        char typekind                   # kind in array --- character code of typestr
        int itemsize                    # size of each element
        int flags                       # flags indicating how the data should be interpreted
        unsigned int *shape              # A length-nd array of shape information
        unsigned int *strides            # A length-nd array of stride information
        void *data                      # A pointer to the first element of the array

    ctypedef enum PyGenericArray_KINDS:
        PyArrayKind_BOOL
        PyArrayKind_INT
        PyArrayKind_UINT
        PyArrayKind_FLOAT
        PyArrayKind_COMPLEX
        PyArrayKind_STRING
        PyArrayKind_UNICODE
        PyArrayKind_OBJECT
        PyArrayKind_RECORD
        PyArrayKind_VOID
        PyArrayKind_BIT
        PyArrayKind_OTHER

    ctypedef enum PyArray_FLAGS:
        CONTIGUOUS
        FORTRAN
        ALIGNED
        NOTSWAPPED
        WRITEABLE

    cdef double* PyArrayInterface_DATA_AS_DOUBLE_C_ARRAY(PyGenericArrayInterface* )
    cdef double* PyArrayInterface_DATA_AS_DOUBLE_C_ARRAY_RO(PyGenericArrayInterface* )

    cdef int PyArrayInterface_IS_C_ARRAY(PyGenericArrayInterface* )
    cdef int PyArrayInterface_IS_C_ARRAY_RO(PyGenericArrayInterface* )

    cdef int PyArrayInterface_CHECK(PyGenericArrayInterface* )
    cdef int PyArrayInterface_CHECK_1D(PyGenericArrayInterface* )
    cdef int PyArrayInterface_CHECK_2D(PyGenericArrayInterface* )

    cdef int PyArrayInterface_SHAPE(PyGenericArrayInterface*, int)

