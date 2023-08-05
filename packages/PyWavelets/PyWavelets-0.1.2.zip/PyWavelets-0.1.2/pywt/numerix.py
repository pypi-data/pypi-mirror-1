from array import array as array_array

use_numpy_flag = False

min_numpy_version = [0, 9, 4]
def use_numpy(use = None):
    """
    Use numpy version 0.9.4 or greater if installed.
    
    use_numpy(use = None) -> bool
        use - True  - use numpy
            - False - use standard Python builtins
            - None  - check status
    """
    global use_numpy_flag
    if use is not None:
        if use:
            try:
                import numpy
                use_numpy_flag = map(int, numpy.__version__.split('.')) >= min_numpy_version
            except ImportError:
                use_numpy_flag = 0
        else:
            use_numpy_flag = 0
    return use_numpy_flag

if use_numpy(True):
    from numpy import array, asarray, zeros, Float64

def contiguous_array_from_any(source):
    global use_numpy_flag
    if use_numpy_flag:
		return array(source, Float64, ndmin=1) # ensure contiguous
    else:
        return array_array('d', source)

def memory_buffer_object(size):
    global use_numpy_flag
    if use_numpy_flag:
        return zeros((size,), Float64)
    else:
        return array_array('d', [0.]) * size


###############################################################################
# 2D buffer object creaating
#
#def memory_buffer_object2D(x, y):
#    global use_numpy_flag
#    if use_numpy_flag:
#        return zeros((x,y), Float64)
#    else:
#        None
