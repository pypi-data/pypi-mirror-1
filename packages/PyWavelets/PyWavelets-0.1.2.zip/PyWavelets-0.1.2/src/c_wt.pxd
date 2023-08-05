cdef extern from "wt.h":

    ctypedef enum MODE:
        MODE_INVALID = -1
        MODE_ZEROPAD = 0
        MODE_SYMMETRIC
        MODE_ASYMMETRIC
        MODE_CONSTANT_EDGE
        MODE_SMOOTH
        MODE_PERIODIC
        MODE_PERIODIZATION
        MODE_MAX

    ctypedef enum SYMMETRY:
        ASYMMETRIC
        NEAR_SYMMETRIC
        SYMMETRIC

    ctypedef struct Wavelet:
        double* dec_hi      # highpass decomposition
        double* dec_lo      # lowpass   decomposition
        double* rec_hi      # highpass reconstruction
        double* rec_lo      # lowpass   reconstruction
                
        int dec_len         # length of decomposition filter
        int rec_len         # length of reconstruction filter

        int dec_hi_offset
        int dec_lo_offset
        int rec_hi_offset
        int rec_lo_offset

        int vanishing_moments_psi
        int vanishing_moments_phi
        int support_width

        int orthogonal
        int biorthogonal
        int orthonormal

        int symmetry

        int compact_support

        int _builtin

        char* family_name
        char* short_name



    cdef void* wtmalloc(long size)
    cdef void* wtcalloc(long len, long size)
    cdef void wtfree(void* ptr)

    cdef Wavelet* wavelet(char name, int type)
    cdef Wavelet* blank_wavelet(int filter_length)
    cdef void free_wavelet(Wavelet* wavelet)

    cdef int dwt_buffer_length(int input_len, int filter_len, MODE mode)
    cdef int upsampling_buffer_length(int coeffs_len, int filter_len, MODE mode)
    cdef int idwt_buffer_length(int coeffs_len, int filter_len, MODE mode)
    cdef int swt_buffer_length(int coeffs_len)

    cdef int reconstruction_buffer_length(int coeffs_len, int filter_len)

    cdef int dwt_max_level(int input_len, int filter_len)

    cdef int d_dec_a(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int mode)
    cdef int d_dec_d(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int mode)

    cdef int d_rec_a(double coeffs_a[], int coeffs_len, Wavelet* wavelet, double output[], int output_len)
    cdef int d_rec_d(double coeffs_d[], int coeffs_len, Wavelet* wavelet, double output[], int output_len)

    cdef int d_idwt(double coeffs_a[], int coeffs_a_len, double coeffs_d[], int coeffs_d_len, Wavelet* wavelet, double output[], int output_len, int mode, int correct_size)

    cdef int max_swt_level(int input_len)
    cdef int d_swt_a(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int level)
    cdef int d_swt_d(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int level)

