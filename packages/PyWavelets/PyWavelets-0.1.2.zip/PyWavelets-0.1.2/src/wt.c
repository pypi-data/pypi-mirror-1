#include "wt.h"

int d_dec_a(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int mode){
	if(output_len != dwt_buffer_length(input_len, wavelet->dec_len, mode)){
		return -1;
	}
	return downsampling_convolution(input, input_len, wavelet->dec_lo, wavelet->dec_len, output, 2, mode);
}

int d_dec_d(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int mode){
	if(output_len != dwt_buffer_length(input_len, wavelet->dec_len, mode))
		return -1;
	return downsampling_convolution(input, input_len, wavelet->dec_hi, wavelet->dec_len, output, 2, mode);
}

int d_rec_a(double coeffs_a[], int coeffs_len, Wavelet* wavelet, double output[], int output_len){
	if(output_len != reconstruction_buffer_length(coeffs_len, wavelet->rec_len))
		return -1;
	
	return upsampling_convolution_full(coeffs_a, coeffs_len, wavelet->rec_lo, wavelet->rec_len, output, output_len);
}

int d_rec_d(double coeffs_d[], int coeffs_len, Wavelet* wavelet, double output[],int  output_len){
	if(output_len != reconstruction_buffer_length(coeffs_len, wavelet->rec_len))
		return -1;
	
	return upsampling_convolution_full(coeffs_d, coeffs_len, wavelet->rec_hi, wavelet->rec_len, output, output_len);
}

// from numerical recipies
unsigned long igray(unsigned long n, int is)
//For zero or positive values of is, return the Gray code of n; if is is negative, return the inverse
//Gray code of n.
{
	int ish;
	unsigned long ans,idiv;
	if (is >= 0)
		return n ^ (n >> 1);
	ish=1; 
	ans=n;
	for (;;) {
		ans ^= (idiv=ans >> ish);
		if (idiv <= 1 || ish == 16) return ans;
		ish <<= 1; 
	}
}

int d_idwt(double coeffs_a[], int coeffs_a_len, double coeffs_d[], int coeffs_d_len, Wavelet* wavelet, double output[],
		 int output_len, int mode, int correct_size)
{
	int input_len;
	
	if(coeffs_a != NULL && coeffs_d != NULL){
		if(correct_size){
			if( (coeffs_a_len > coeffs_d_len ? coeffs_a_len - coeffs_d_len : coeffs_d_len-coeffs_a_len) > 1) // abs(a-b)
				return -1;
			input_len = coeffs_a_len>coeffs_d_len? coeffs_d_len : coeffs_a_len; // min
		} else {
			if(coeffs_a_len != coeffs_d_len)
				return -1;
			input_len = coeffs_a_len;
		}
	} else if(coeffs_a != NULL){
		input_len  = coeffs_a_len;
	} else if (coeffs_d != NULL){
		input_len = coeffs_d_len;
	} else {
		return -1;
	}
	
	if(output_len != idwt_buffer_length(input_len, wavelet->rec_len, mode)) return -1;
	memset(output, 0, output_len * sizeof(double));

	if(coeffs_a){
		if(upsampling_convolution_valid_sf(coeffs_a, input_len, wavelet->rec_lo, wavelet->rec_len, output, output_len, mode) < 0)
			return -1;
	}
	// +=
	if(coeffs_d){
		if(upsampling_convolution_valid_sf(coeffs_d, input_len, wavelet->rec_hi, wavelet->rec_len, output, output_len, mode) < 0)
			return -1;
	}
	return 0;
}

__inline int d_swt_(double input[], int input_len, const double filter[], int filter_len, double output[], int output_len, int level){
	double* e_filter;
	int i, e_filter_len;

	if(level < 1)
		return -1;
	else if(level > max_swt_level(input_len))
		return -2;

	if(output_len != swt_buffer_length(input_len))
		return -1;

	// TODO: quick hack, optimize
	if(level > 1){
		e_filter_len = filter_len << (level-1);
		e_filter = wtcalloc(e_filter_len, sizeof(double));
		if(e_filter == NULL)
			return -1;

		// make up extended filter
		for(i = 0; i < filter_len; ++i){
			e_filter[i << (level-1)] = filter[i];
		}
		i = downsampling_convolution(input, input_len, e_filter, e_filter_len, output, 1, MODE_PERIODIZATION);
		wtfree(e_filter);
		return i;

	} else {
		return downsampling_convolution(input, input_len, filter, filter_len, output, 1, MODE_PERIODIZATION);
	}
}

int d_swt_a(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int level){
	return d_swt_(input, input_len, wavelet->dec_lo, wavelet->dec_len, output, output_len, level);
}

int d_swt_d(double input[], int input_len, Wavelet* wavelet, double output[], int output_len, int level){
	return d_swt_(input, input_len, wavelet->dec_hi, wavelet->dec_len, output, output_len, level);
}
