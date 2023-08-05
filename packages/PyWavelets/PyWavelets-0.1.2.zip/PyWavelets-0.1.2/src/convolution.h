#ifndef _CONVOLUTION_H_
#define _CONVOLUTION_H_

#include <stdlib.h>
#include <stdio.h>
#include <memory.h>
#include <math.h>

enum MODE {
	   MODE_INVALID = -1,
       MODE_ZEROPAD = 0, // default
       MODE_SYMMETRIC,
	   MODE_ASYMMETRIC,
	   MODE_CONSTANT_EDGE,
       MODE_SMOOTH,
	   MODE_PERIODIC,
	   MODE_PERIODIZATION,
	   MODE_MAX
};

#define wtmalloc(size_t) malloc(size_t)
#define wtcalloc(len, size_t) calloc(len, size_t)
#define wtfree(ptr) free(ptr)


int dwt_buffer_length(int input_len, int filter_len, int mode);
int reconstruction_buffer_length(int coeffs_len, int filter_len);
int idwt_buffer_length(int coeffs_len, int filter_len, int mode);
int swt_buffer_length(int input_len);


int dwt_max_level(int input_len, int filter_len);


///////////////////////////////////////////////////////////////////////////////
//
// performs convolution of input with filter and downsamples by taking every
// step-th element from result.
//
// input	- input vector
// N		- input vector length
// filter	- filter vector
// F		- filter vector length
// output	- output vector
// step		- downsample step
// mode		- 

#define DTYPE double

int downsampling_convolution(const DTYPE* input, const int N, const double* filter, const int F, double* output, const int step, const int mode);
int allocating_downsampling_convolution(const DTYPE* input, const int N, const double* filter, const int F, double* output, const int step, const int mode);

#define convolution(data, data_len, filter, filter_len, output) downsampling_convolution(data, data_len, filter, filter_len, output, 1, MODE_ZEROPAD);


///////////////////////////////////////////////////////////////////////////////
//
// upsamples input signal by inserting zeros and convolves with filter.
// input: i0 i1 i2 i3 -> (upsampling) -> i0 0 i1 0 i2 0 i3 (0)
//
// input	- input vector
// N		- input vector length
// filter	- filter vector
// F		- filter vector length
// output	- output vector
// mode		- 


int upsampling_convolution_full(const DTYPE* input, const int N, const double* filter, const int F, double* output, const int O);
int upsampling_convolution_valid_sf(const DTYPE* input, const int N, const double* filter, const int F, double* output, const int O, const int mode);

//TODO
//int extended_filter_convolution(const DTYPE* input, const int N, const double* filter, const int F, double* output, int step, int mode);

#endif
