###############################################################################
# Copyright (C): 2006 Filip Wasilewski <filipwasilewski@gmail.com>            #
# License:       MIT                                                          #
############################################################################### 

__version__ = "0.1.2"

###############################################################################
# cimports

cimport c_python
cimport c_array_interface
cimport c_wt
cimport c_math

###############################################################################
# array.array

import array
cdef object array_array_type
array_array_type = array.array

from numerix import contiguous_array_from_any, memory_buffer_object


###############################################################################
# buffer objects handling

cdef int array_interface_as_double_array_ptr(object source, unsigned int min_dims, double** buffer_addr, int* buffer_len, int mode):
    """
    Get object buffer for reading (mode = 'r') or writing (mode = 'w')

    source      - source object exposing array interfce
    buffer_addr - will be set on success
    data_len    - buffer length
    mode        - read/write mode

    returns     -  0 - ok
                - -1 - no __array_struct__ attr
                - -2, -3, -4 - other errors 
    """

    # todo, remove debug info when ready
    
    cdef double* data
    cdef int data_len, data_len2
    cdef c_array_interface.PyGenericArrayInterface* array_struct
    cdef object cobject

    if hasattr(source, '__array_struct__'):
        cobject = source.__array_struct__
        if c_python.PyCObject_Check(cobject):
            array_struct = <c_array_interface.PyGenericArrayInterface*> c_python.PyCObject_AsVoidPtr(cobject)

            if min_dims == 1:
                if not (c_array_interface.PyArrayInterface_CHECK_1D(array_struct)):
                    #print "not 1D"
                    return -3
                data_len = c_array_interface.PyArrayInterface_SHAPE(array_struct, 0)
                if data_len < 1:
                    #print "data len < 1"
                    return -5
                buffer_len[0] = data_len
            elif min_dims == 2:
                if not (c_array_interface.PyArrayInterface_CHECK_2D(array_struct)):
                    #print "not 2D"
                    return -3
                data_len = c_array_interface.PyArrayInterface_SHAPE(array_struct, 0)
                data_len2 = c_array_interface.PyArrayInterface_SHAPE(array_struct, 1)
                if data_len < 1 or data_len2 < 1:
                    #print "datalen or datalen2 < 1"
                    return -5
                buffer_len[0] = data_len
                buffer_len[1] = data_len2
            else:
                #print "invalid min dim"
                return -4

			#print "C_RO", c_array_interface.PyArrayInterface_IS_C_ARRAY_RO(array_struct)

            if mode == c'w':
                data = c_array_interface.PyArrayInterface_DATA_AS_DOUBLE_C_ARRAY(array_struct)
            elif mode == c'r':
                data = c_array_interface.PyArrayInterface_DATA_AS_DOUBLE_C_ARRAY_RO(array_struct)
            else:
                #print "invalid mode"
                return -6

            if data != NULL:
                buffer_addr[0] = data
                return 0
            else:
                #print "not C double array" # type is not double, array is not c-contiguous or data is NULL
                #print <int> array_struct.data
                #print array_struct.nd
                #print array_struct.typekind
                #print array_struct.itemsize
                #print array_struct.flags
                return -7

        #print "not cobject"
        return -2
    #print "no __array_struct__ attr"
    return -1

cdef int array_array_object_as_double_buffer_ptr(object source, double** buffer_addr, int* buffer_len, int mode):
    """
    Get object buffer for reading (mode = 'r') or writing (mode = 'w')

    source      - source object
    buffer_addr - will be set on success
    data_len    - buffer length
    mode        - read/write mode

    returns     - -1 - invalid data type
                -  0 - ok
    """

    cdef void* data
    cdef double* d_data
    cdef int n, data_len
   
    if source.typecode != 'd':
        return -2

    n = len(source)
    if n < 1:
        return -1
        
    if mode == c'r':
        if c_python.PyObject_AsReadBuffer(source, &data, &data_len):
            return -1
    elif mode == c'w':
        if c_python.PyObject_AsWriteBuffer(source, &data, &data_len):
            return -1
    
    buffer_len[0] = n
    buffer_addr[0] = <double*> data
    return 0

cdef int object_as_buffer(object source, double** buffer_addr, int* buffer_len, int mode):
    if type(source) != array_array_type:
        # array interface
        return array_interface_as_double_array_ptr(source, 1, buffer_addr, buffer_len, mode)
    else:
        # python array.array object
        return array_array_object_as_double_buffer_ptr(source, buffer_addr, buffer_len, mode)

cdef int object_as_buffer2D(object source, double** buffer_addr, int* buffer_len, int mode):
    return array_interface_as_double_array_ptr(source, 2, buffer_addr, buffer_len, mode)

###############################################################################
#

cdef object double_array_to_list(double* data, int n):
    cdef int i
    ret = []
    for i from 0 <= i < n:
        ret.append(data[i])
    return ret

#cdef c_numerix.ndarray double_array_to_ndarray(double* data, int n):
#    cdef int dims[1]
#    dims[0] = n
#    return c_numerix.PyArray_SimpleNewFromData(1, dims, c_numerix.PyArray_DOUBLE, <char*>data)

cdef object double_array_to_object(double* data, int n):
    return double_array_to_list(data, n)

cdef int copy_object_to_double_array(source, double* dest) except -1:
    cdef int i
    cdef int n
    try:
        n = len(source)
        for i from 0 <= i < n:
            dest[i] = source[i]
    except Exception, e:
        raise e
        return -1
    return 0

###############################################################################
# MODES

def __from_str(cls, s):
    if s in cls.modes and hasattr(cls, s):
        return getattr(cls, s)
    else:
        raise ValueError, "Unknown mode name"

class MODES(object):
    """
    Different ways of dealing with border distortion problem while performing
    Discrete Wavelet Transform analysis.
    
    To reduce this effect the signal or image can be extended by adding extra samples.
    
    zpd - zero-padpadding                0  0 | x1 x2 ... xn | 0  0
    cpd - constant-padding              x1 x1 | x1 x2 ... xn | xn xn
    sym - symmetric-padding             x2 x1 | x1 x2 ... xn | xn xn-1
    ppd - periodic-padding            xn-1 xn | x1 x2 ... xn | x1 x2
    sp1 - smooth-padding               (1st derivative interpolation)
    
    DWT performed for these extension modes is slightly redundant, but ensure
    a perfect reconstruction for IDWT.

    per - periodization - like periodic-padding but gives the smallest number
          of decomposition coefficients. IDWT must be performed with the same mode.
          
    """
    
    zpd = c_wt.MODE_ZEROPAD
    cpd = c_wt.MODE_CONSTANT_EDGE
    sym = c_wt.MODE_SYMMETRIC
    ppd = c_wt.MODE_PERIODIC
    sp1 = c_wt.MODE_SMOOTH
    per = c_wt.MODE_PERIODIZATION
    
    _asym = c_wt.MODE_ASYMMETRIC
    
    modes = ["zpd", "cpd", "sym", "ppd", "sp1", "per"]

    from_str = classmethod(__from_str)

###############################################################################
# Wavelet

cdef wname_to_code(char* name):
    name_ = name.lower()
    
    if len(name_) == 0:
        raise ValueError("Invalid wavelet name")

    for n, code in (("db", c"d"), ("sym", c"s"), ("coif", c"c")):
        if name_[:len(n)] == n:
            try:
                number = int(name_[len(n):])
                return (code, number)
            except ValueError:
                pass

    if name_[:4] == "bior":
        if len(name_) == 7 and name_[-2] == '.':
            try:
                number = int(name_[-3])*10 + int(name_[-1])
                return (c'b', number)
            except ValueError:
                pass
    elif name_[:4] == "rbio":
        if len(name_) == 7 and name_[-2] == '.':
            try:
                number = int(name_[-3])*10 + int(name_[-1])
                return (c'r', number)
            except ValueError:
                pass
    elif name_ == "haar":
        return c'h', 0

    elif name_ == "dmey":
        return c'm', 0

    raise ValueError("Unknown wavelet name, '%s' not in wavelist()" % name)

cdef public class Wavelet [type WaveletType, object WaveletObject]:
    cdef c_wt.Wavelet* w
    cdef readonly name
    cdef readonly number
 
    def __new__(self, char* name="", object filterBank=None):
        cdef int i

        if not name and filterBank is None:
            raise TypeError("Wavelet name or filter bank not specified")
        #print wname_to_code(name, number)

        if filterBank is None:
            # builtin wavelet
            c, nr = wname_to_code(name)
            self.w = <c_wt.Wavelet*> c_wt.wavelet(c, nr)

            if self.w == NULL:
                raise ValueError("Wrong wavelet name")

            self.name = name.lower()
            self.number = nr

        else:
            filters = filterBank.get_filters_coeffs()
            if len(filters) != 4:
                raise ValueError("Expected filter bank with 4 filters, got filter bank with %d filters" % len(filters))

            try:
                dec_lo = array_array_type('d', filters[0])
                dec_hi = array_array_type('d', filters[1])
                rec_lo = array_array_type('d', filters[2])
                rec_hi = array_array_type('d', filters[3])
            except TypeError:
                raise TypeError("Filter bank with float or int values is required")

            max_length = max(len(dec_lo), len(dec_hi), len(rec_lo), len(rec_hi))
            if max_length == 0:
                raise ValueError("Filter bank is zero-length")

            self.w = <c_wt.Wavelet*> c_wt.blank_wavelet(max_length)
            if self.w == NULL:
                raise ValueError("Could not allocate memory for given filter bank")

            # copy values to struct
            copy_object_to_double_array(dec_lo, self.w.dec_lo)
            copy_object_to_double_array(dec_hi, self.w.dec_hi)
            copy_object_to_double_array(rec_lo, self.w.rec_lo)
            copy_object_to_double_array(rec_hi, self.w.rec_hi)
            
            self.name = name

    def __dealloc__(self):
        if self.w != NULL:
            c_wt.free_wavelet(self.w) # if w._builtin is 0, it frees also the filter arrays
            self.w = NULL

    def __len__(self): #assume
        return self.dec_len

    property dec_lo:
        def __get__(self):
            return double_array_to_object(self.w.dec_lo, self.w.dec_len)

    property dec_hi:
        def __get__(self):
            return double_array_to_object(self.w.dec_hi, self.w.dec_len)

    property rec_lo:
        def __get__(self):
            return double_array_to_object(self.w.rec_lo, self.w.rec_len)

    property rec_hi:
        def __get__(self):
            return double_array_to_object(self.w.rec_hi, self.w.rec_len)

    property rec_len:
        def __get__(self):
            return self.w.rec_len

    property dec_len:
        def __get__(self):
            return self.w.dec_len

    property family_name:
        def __get__(self):
            return self.w.family_name

    property short_name:
        def __get__(self):
            return self.w.short_name

    property orthogonal:
        def __get__(self):
            return bool(self.w.orthogonal)

    property biorthogonal:
        def __get__(self):
            return bool(self.w.biorthogonal)

    property orthonormal:
        def __get__(self):
            return bool(self.w.orthonormal)
    
    property symmetry:
        def __get__(self):
            if self.w.symmetry == c_wt.ASYMMETRIC:
                return "asymmetric"
            elif self.w.symmetry == c_wt.NEAR_SYMMETRIC:
                return "near symmetric"
            elif self.w.symmetry == c_wt.SYMMETRIC:
                return "symmetric"
            else:
                return "unknown"

    property vanishing_moments_psi:
        def __get__(self):
            if self.w.vanishing_moments_psi > 0:
                return self.w.vanishing_moments_psi

    property vanishing_moments_phi:
        def __get__(self):
            if self.w.vanishing_moments_phi > 0:
                return self.w.vanishing_moments_phi

    property _builtin:
        def __get__(self):
            return bool(self.w._builtin)

    def filters(self):
        print DeprecationWarning("Wavelet.filters() function is depreciated, use Wavelet.get_filters_coeffs() instead")
        return self.get_filters()

    def get_filters_coeffs(self):
        return (self.dec_lo, self.dec_hi, self.rec_lo, self.rec_hi)

    def wavefun(self, int level=3):
        cdef double coef "coef"
        cdef double pas "pas"
        coef = c_math.pow(c_math.sqrt(2.), <double>level)
        pas  = 1./(c_math.pow(2., <double>level))
        
        if self.short_name == "sym" or self.short_name == "coif":
            return upcoef('a', [coef], self, level), upcoef('d', [-coef], self, level)
        elif self.short_name in ("bior", "rbio"):
            if self.short_name == "bior":
                other_name = "rbio" + self.name[4:]
            elif self.short_name == "rbio":
                other_name = "bior" + self.name[4:]
            other = Wavelet(other_name)
            return upcoef('a', [1], self, level), upcoef('d', [1], self, level), upcoef('a', [1], other, level), upcoef('d', [1], other, level)
        else:
            return upcoef('a', [coef], self, level), upcoef('d', [coef], self, level)

    def __str__(self):
        return "Wavelet %s\n" \
        "  Family name:    %s\n" \
        "  Short name:     %s\n" \
        "  Filters length: %d\n" \
        "  Orthogonal:     %s\n" \
        "  Biorthogonal:   %s\n" \
        "  Orthonormal:    %s\n" \
        "  Symmetry:       %s" % \
        (self.name, self.family_name, self.short_name, self.dec_len, self.orthogonal, self.biorthogonal, self.orthonormal, self.symmetry)

###############################################################################
#

def dwt_max_level(int data_len, int filter_len):
    return c_wt.dwt_max_level(data_len, filter_len)

###############################################################################
# dwt 

def dwt(object data, object wavelet, object mode=c_wt.MODE_SYMMETRIC):
    """
    (cA, cD) = dwt(data, wavelet, mode=MODES.sym)

    Single level Discrete Wavelet Transform

    data    - input signal
    wavelet - wavelet to use (Wavelet object or name)
    mode    - signal extension mode, see help(MODES)

    Returns approximation (a) and detail (d) coefficients.

    Length of coefficient arrays depends on mode selected:

        for all modes except 'periodization' (MODES.per)
            len(a) == len(d) == floor((len(data) + wavelet.dec_len - 1) / 2)

        for 'periodization' mode:
            len(a) == len(d) == ceil(len(data) / 2)
    """

    cdef double* input_data
    cdef double* output_data
    
    cdef int input_len
    cdef int output_len
    cdef int mode_
    cdef Wavelet w
    
    cdef alternative_data
    cdef object coeff_a
    cdef object coeff_d

    cdef int i

    # mode
    if type(mode) is int:
        if mode <= c_wt.MODE_INVALID or mode >= c_wt.MODE_MAX:
            raise ValueError("Invalid mode, see MODES")
        mode_ = mode
    else:
        mode_ = MODES.from_str(mode)

    # input as array
    if object_as_buffer(data, &input_data, &input_len, c'r') < 0:
        alternative_data = contiguous_array_from_any(data)
        if object_as_buffer(alternative_data, &input_data, &input_len, c'r'):
            raise TypeError("Invalid data type, 1D array or iterable object required")
    if input_len < 1:
        raise ValueError, "Invalid input length (len(data) < 1)"

    # wavelet
    if type(wavelet) is Wavelet:
        w = wavelet
    else:
        w = Wavelet(wavelet)
    
    # output len
    output_len = c_wt.dwt_buffer_length(input_len, w.dec_len, mode_)
    if output_len < 1:
        raise RuntimeError("Invalid output length")

    # decompose A
    coeff_a = memory_buffer_object(output_len)
    if object_as_buffer(coeff_a, &output_data, &output_len, c'w') < 0:
        raise RuntimeError, "Getting data pointer for buffer failed"
    if c_wt.d_dec_a(input_data, input_len, w.w, output_data, output_len, mode_) < 0:
        raise RuntimeError, "C dwt failed"
   
    # decompose D
    coeff_d = memory_buffer_object(output_len)
    if object_as_buffer(coeff_d, &output_data, &output_len, c'w') < 0:
        raise RuntimeError, "Getting data pointer for buffer failed"
    if c_wt.d_dec_d(input_data, input_len, w.w, output_data, output_len, mode_) < 0:
        raise RuntimeError, "C dwt failed"
 
    # return
    return (coeff_a, coeff_d)


def dwt_coeff_len(int data_len, int filter_len, object mode):
    """
    dwt_coeff_len(int data_len, int filter_len, mode) -> int

    Returns length of dwt output for given data length, filter length and mode.
    """
    if data_len < 1:
        raise ValueError, "data_len must be > 0"
    if filter_len < 1:
        raise ValueError, "data_len must be > 0"

    if type(mode) is int:
        if mode <= c_wt.MODE_INVALID or mode >= c_wt.MODE_MAX:
            raise ValueError("Invalid mode")
    else:
        mode = MODES.from_str(mode)
   
    return c_wt.dwt_buffer_length(data_len, filter_len, <int>mode)

###############################################################################
# idwt

def idwt(object coeff_a, object coeff_d, object wavelet, object mode_ = c_wt.MODE_SYMMETRIC, int correct_size = 0):
    """
    A = idwt(coeff_a, coeff_d, wavelet, mode=MODES.sym, correct_size=0)

    Single level Inverse Discrete Wavelet Transform

    coeff_a - approximation coefficients
    coeff_d - detail coefficients
    wavelet - wavelet to use (Wavelet object or name)
    mode    - signal extension mode, see MODES

    correct_size - additional option. Normally coeff_a and coeff_d must have
        the same length, with correct_size set to True, length of coeff_a may
        be greater by 1 than length of coeff_d. This is useful when doing
        multilevel reconstructions of non-dyadic length signals.
    
    Returns single level reconstruction of signal from given coefficients.

    Length of coefficient arrays depends on mode selected:

        for all modes except 'periodization' (MODES.per)
            len(a) == len(d) == floor((len(data) + wavelet.dec_len - 1) / 2)

        for 'periodization' mode:
            len(a) == len(d) == ceil(len(data) / 2)

    """

    cdef double *input_data_a, *input_data_d
    cdef double* reconstruction_data
 
    cdef int input_len_a, input_len_d, input_len
    cdef int reconstruction_len

    cdef Wavelet w
    
    cdef object alternative_data_a, alternative_data_d, reconstruction

    cdef int i, ret, mode

    input_data_a = input_data_d = NULL
    input_len_a = input_len_d = 0

    if type(mode_) is int:
        mode = mode_
        if mode <= c_wt.MODE_INVALID or mode >= c_wt.MODE_MAX:
            raise ValueError("Invalid mode")
    else:
        mode = MODES.from_str(mode_)

    if type(wavelet) is Wavelet:
        w = wavelet
    else:
        w = Wavelet(wavelet)

    if coeff_a is None and coeff_d is None:
        raise ValueError, "Coeffs not specified"

    # get data pointer and size
    if coeff_a is not None:
        if object_as_buffer(coeff_a, &input_data_a, &input_len_a, c'r') < 0:
            alternative_data_a = contiguous_array_from_any(coeff_a)
            if object_as_buffer(alternative_data_a, &input_data_a, &input_len_a, c'r'):
                raise TypeError("Invalid coeff_a type")
        if input_len_a < 1:
            raise ValueError, "len(coeff_a) < 1"

    # get data pointer and size
    if coeff_d is not None:
        if object_as_buffer(coeff_d, &input_data_d, &input_len_d, c'r') < 0:
            alternative_data_d = contiguous_array_from_any(coeff_d)
            if object_as_buffer(alternative_data_d, &input_data_d, &input_len_d, c'r'):
                raise TypeError("Invalid coeff_d type")
        if input_len_d < 1:
            raise ValueError, "len(coeff_d) < 1"

    # check if sizes differ
    cdef int diff
    if input_len_a > 0:
        if input_len_d > 0:
            diff = input_len_a - input_len_d
            if correct_size:
                if diff < 0 or diff > 1:
                    raise ValueError, "Coefficient arrays lengths differs too much"
                input_len = input_len_a -diff
            elif diff:
                raise ValueError, "Coefficient arrays must have the same size"
            else:
                input_len = input_len_d
        else:
            input_len = input_len_a
    else:
        input_len = input_len_d

    # find buffer length
    reconstruction_len = c_wt.idwt_buffer_length(input_len, w.rec_len, mode)
    if reconstruction_len < 1:
        raise ValueError("Invalid coefficient arrays length for specified wavelet. Probably reconstructing not a result of dwt or the wavelet or mode is mistaken.")

    # allocate buffer
    reconstruction = memory_buffer_object(reconstruction_len)

    # get buffer's data pointer and len
    if object_as_buffer(reconstruction, &reconstruction_data, &reconstruction_len, c'w') < 0:
        raise RuntimeError, "Getting data pointer for buffer failed"

    # call idwt func
    # one of input_data_a/input_data_d can be NULL, then only reconstruction of non-null part will be performed
    if c_wt.d_idwt(input_data_a, input_len_a, input_data_d, input_len_d, w.w, reconstruction_data, reconstruction_len, mode, correct_size) < 0:
        raise RuntimeError, "C idwt failed"
 
    return reconstruction

###############################################################################
#

def upcoef(part, coef, wavelet, int level=1, int take=0):
    cdef double *input_data
    cdef double* reconstruction_data
 
    cdef int input_len
    cdef int reconstruction_len

    cdef Wavelet w
    
    cdef object data, alternative_data, reconstruction
    cdef int i, rec_a
    cdef int left_bound, right_bound

    input_data = NULL
    input_len = 0

    if part not in ('a', 'd'):
        raise ValueError("Arument 1 must be 'a' or 'd' not %s" % part)
    rec_a = 0
    if part == 'a':
        rec_a = 1

    if type(wavelet) is Wavelet:
        w = wavelet
    else:
        w = Wavelet(wavelet)

    if level < 1:
        raise ValueError("level must be greater than 0")

    # input as array
    if object_as_buffer(coef, &input_data, &input_len, c'r') < 0:
        alternative_data = contiguous_array_from_any(coef)
        if object_as_buffer(alternative_data, &input_data, &input_len, c'r'):
            raise TypeError("Invalid data type, 1D array or iterable required")
    if input_len < 1:
        raise ValueError, "Invalid input length (len(data) < 1)"

    for i from 0 <= i < level:
        # output len
        reconstruction_len = c_wt.reconstruction_buffer_length(input_len, w.dec_len)
        if reconstruction_len < 1:
            raise RuntimeError("Invalid output length")

        # reconstruct
        reconstruction = memory_buffer_object(reconstruction_len)
        if object_as_buffer(reconstruction, &reconstruction_data, &reconstruction_len, c'w') < 0:
            raise RuntimeError, "Getting data pointer for buffer failed"

        if rec_a:
            if c_wt.d_rec_a(input_data, input_len, w.w, reconstruction_data, reconstruction_len) < 0:
                raise RuntimeError, "C rec_a failed"
        else:
            if c_wt.d_rec_d(input_data, input_len, w.w, reconstruction_data, reconstruction_len) < 0:
                raise RuntimeError, "C rec_d failed"
        rec_a = 1

        data = reconstruction # keep reference
        input_len = reconstruction_len
        input_data = reconstruction_data

    if take > 0:
        if take < reconstruction_len:
            left_bound = right_bound = (reconstruction_len-take)/2
            if (reconstruction_len-take)%2:
                left = left + 1

            return reconstruction[left_bound:-right_bound]

    return reconstruction

###############################################################################
# multilevel transform

def waverec(object coeffs_list, object wavelet, object mode=c_wt.MODE_SYMMETRIC):
    """
    waverec(object coeffs_list, object wavelet, object mode=c_wt.MODE_SYMMETRIC)

    Performs multilevel reconstruction of signal from coefficient list.

    coeffs_list - coefficient list [cAn aDn cDn-1 ... cD2 cD1]
    wavelet - wavelet to use (Wavelet object or name)
    mode    - signal extension mode, see MODES
    """
    if type(coeffs_list) not in (tuple, list):
        raise TypeError, "Expected tuple or list of coefficient arrays"
    if len(coeffs_list) < 2:
        raise ValueError, "Coefficient list too short (minimum 2 arrays required)"

    a, ds = coeffs_list[0], coeffs_list[1:]
    for d in ds:
        a = idwt(a, d, wavelet, mode, 1)
    return a

def wavedec(object data, object wavelet, int level=1, object mode=c_wt.MODE_SYMMETRIC):
    """
    wavedec(object data, object wavelet, int level=1, object mode=c_wt.MODE_SYMMETRIC)

    Performs multilevel Discrete Wavelet Transform decomposition of given signal.
    Returns coefficient list - [cAn cDn cDn-1 ... cD2 cD1]

    data    - input signal
    wavelet - wavelet to use (Wavelet object or name)
    mode    - signal extension mode, see MODES
    """
    cdef int i
    cdef object coeffs_list

    if level < 1:
        raise ValueError, "Level value is too low '%d'. Minimum '1' required." % level

    coeffs_list = []

    a = data
    for i from 0 <= i < level:
        a, d = dwt(a, wavelet, mode)
        coeffs_list.append(d)
    coeffs_list.append(a)
    coeffs_list.reverse()
    return coeffs_list

###############################################################################
# swt

def swt_max_level(int input_len):
    """
    swt_max_level(int input_len)

    Returns maximum level of Stationary Wavelet Transform for data of given length.
    """
    return c_wt.max_swt_level(input_len)

def swt(object data, object wavelet, int level):
    """
    swt(object data, object wavelet, int level)
    
    Performs multilevel Stationary Wavelet Transform.

    data    - input signal
    wavelet - wavelet to use (Wavelet object or name)
    level   - transform level

    Returns list of coefficient pairs in form
        [(cA1, cD1), (cA2, cD2), ..., (cAn, cDn)], where n = level
    """
    cdef double* input_data
    cdef double* output_data
    
    cdef int input_len
    cdef int output_len
    cdef Wavelet w
    
    cdef alternative_data
    cdef object coeff_a
    cdef object coeff_d

    cdef int i

    # input
    if object_as_buffer(data, &input_data, &input_len, c'r') < 0:
        alternative_data = contiguous_array_from_any(data)
        if object_as_buffer(alternative_data, &input_data, &input_len, c'r'):
            raise TypeError("Invalid data type, 1D array or iterable object required")
    if input_len < 1:
        raise ValueError, "Invalid input data length"
    elif input_len % 2:
        raise ValueError, "Length of data must be even"

    # wavelet
    if type(wavelet) is Wavelet:
        w = wavelet
    else:
        w = Wavelet(wavelet)

    # level
    if level < 1:
        raise ValueError("Level must be strictly positive number")
    elif level > c_wt.max_swt_level(input_len):
        raise ValueError("Level value too high (max level for current input len is %d)" % c_wt.max_swt_level(input_len))

    # output length
    output_len = c_wt.swt_buffer_length(input_len)
    if output_len < 1:
        raise RuntimeError("Invalid output length")

    ret = []
    for i from 1 <= i <= level:
        # alloc memory
        coeff_d = memory_buffer_object(output_len)
        coeff_a = memory_buffer_object(output_len)
        
        # decompose D
        if object_as_buffer(coeff_d, &output_data, &output_len, c'w') < 0:
            raise RuntimeError, "Getting data pointer for buffer failed"
        if c_wt.d_swt_d(input_data, input_len, w.w, output_data, output_len, i) < 0:
            raise RuntimeError, "C dwt failed"

        # decompose A
        if object_as_buffer(coeff_a, &output_data, &output_len, c'w') < 0:
            raise RuntimeError, "Getting data pointer for buffer failed"
        if c_wt.d_swt_a(input_data, input_len, w.w, output_data, output_len, i) < 0:
            raise RuntimeError, "C dwt failed"
        input_data = output_data # a -> input
        input_len = output_len

        ret.append((coeff_a, coeff_d))
    return ret

###############################################################################

