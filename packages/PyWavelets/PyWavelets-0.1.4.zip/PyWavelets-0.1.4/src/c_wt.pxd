# Copyright (c) 2006 Filip Wasilewski <filipwasilewski@gmail.com>
# See COPYING for license details.

# $Id: c_wt.pxd 45 2006-07-07 16:15:27Z filipw $

cdef extern from "common.h":

    ctypedef int index_t
    ctypedef index_t const_index_t

    cdef void* wtmalloc(long size)
    cdef void* wtcalloc(long len, long size)
    cdef void wtfree(void* ptr)
    
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


    # buffers lengths
    cdef index_t dwt_buffer_length(index_t input_len, index_t filter_len, MODE mode)
    cdef index_t upsampling_buffer_length(index_t coeffs_len, index_t filter_len, MODE mode)
    cdef index_t idwt_buffer_length(index_t coeffs_len, index_t filter_len, MODE mode)
    cdef index_t swt_buffer_length(index_t coeffs_len)
    cdef index_t reconstruction_buffer_length(index_t coeffs_len, index_t filter_len)

    # max dec levels
    cdef int dwt_max_level(index_t input_len, index_t filter_len)
    cdef int swt_max_level(index_t input_len)


cdef extern from "wavelets.h":

    ctypedef enum SYMMETRY:
        ASYMMETRIC
        NEAR_SYMMETRIC
        SYMMETRIC

    ctypedef struct Wavelet:
        double* dec_hi      # highpass decomposition
        double* dec_lo      # lowpass   decomposition
        double* rec_hi      # highpass reconstruction
        double* rec_lo      # lowpass   reconstruction
                
        index_t dec_len         # length of decomposition filter
        index_t rec_len         # length of reconstruction filter

        index_t dec_hi_offset
        index_t dec_lo_offset
        index_t rec_hi_offset
        index_t rec_lo_offset

        int vanishing_moments_psi
        int vanishing_moments_phi
        index_t support_width

        int orthogonal
        int biorthogonal
        int orthonormal

        int symmetry

        int compact_support

        int _builtin

        char* family_name
        char* short_name


    cdef Wavelet* wavelet(char name, int type)
    cdef Wavelet* blank_wavelet(index_t filter_length)
    cdef void free_wavelet(Wavelet* wavelet)


cdef extern from "wt.h":

    cdef int d_dec_a(double input[], index_t input_len, Wavelet* wavelet, double output[], index_t output_len, MODE mode)
    cdef int d_dec_d(double input[], index_t input_len, Wavelet* wavelet, double output[], index_t output_len, MODE mode)

    cdef int d_rec_a(double coeffs_a[], index_t coeffs_len, Wavelet* wavelet, double output[], index_t output_len)
    cdef int d_rec_d(double coeffs_d[], index_t coeffs_len, Wavelet* wavelet, double output[], index_t output_len)

    cdef int d_idwt(double coeffs_a[], index_t coeffs_a_len, double coeffs_d[], index_t coeffs_d_len, Wavelet* wavelet, double output[], index_t output_len, MODE mode, int correct_size)

    cdef int d_swt_a(double input[], index_t input_len, Wavelet* wavelet, double output[], index_t output_len, int level)
    cdef int d_swt_d(double input[], index_t input_len, Wavelet* wavelet, double output[], index_t output_len, int level)

