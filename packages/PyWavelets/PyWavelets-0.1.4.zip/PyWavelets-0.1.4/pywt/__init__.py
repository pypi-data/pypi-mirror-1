# -*- coding: utf-8 -*-

# Copyright (c) 2006 Filip Wasilewski <filipwasilewski@gmail.com>
# See COPYING for license details.

# $Id: __init__.py 45 2006-07-07 16:15:27Z filipw $

"""
Discrete forward and inverse wavelet transform, stationary wavelet transform,
wavelet packets signal decomposition and reconstruction module.
"""

from _pywt import *
from wnames import *
from multilevel import *
from wavelet_packets import WaveletPacket

del _pywt
del wnames, multilevel, wavelet_packets

from release_details import version as __version__, author as __author__

