# -*- coding: utf-8 -*-

# Copyright (c) 2006 Filip Wasilewski <filipwasilewski@gmail.com>
# See COPYING for license details.

# $Id: numerix.py 45 2006-07-07 16:15:27Z filipw $

"""A thin wrapper for numeric libraries. Modify this to use wavelets with
libraries other than NumPy."""

import warnings

def use_numpy(use = None):
    warnings.warn("use_numpy is deprecatied and array.array are not supported any more", DeprecationWarning)
    
from numpy import array, asarray, zeros, float64

def contiguous_array_from_any(source):
	return array(source, float64, ndmin=1) # ensure contiguous

def memory_buffer_object(size):
    return zeros((size,), float64)

def memory_buffer_object2D(x, y):
     return zeros((x,y), float64)
