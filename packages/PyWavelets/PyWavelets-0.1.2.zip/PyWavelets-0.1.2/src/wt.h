#ifndef _WT_H_
#define _WT_H_

#pragma inline_depth(2)

#include <memory.h>
#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

#include "convolution.h"
#include "wavelets.h"


int d_dec_a(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int mode);
int d_dec_d(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int mode);

int d_rec_a(double coeffs_a[], int coeffs_len, Wavelet* wavelet, double output[], int output_len);
int d_rec_d(double coeffs_d[], int coeffs_len, Wavelet* wavelet, double output[],int  output_len);

int d_idwt(double coeffs_a[], int coeffs_a_len, double coeffs_d[], int coeffs_d_len, Wavelet* wavelet, double output[], int output_len, int mode, int correct_size);

#define max_swt_level(input_len) (int)floor(log(input_len)/log(2))
int d_swt_a(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int level);
int d_swt_d(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int level);

#endif
