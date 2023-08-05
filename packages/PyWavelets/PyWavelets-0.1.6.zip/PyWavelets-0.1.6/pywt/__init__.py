# -*- coding: utf-8 -*-

# Copyright (c) 2006 Filip Wasilewski <filipwasilewski@gmail.com>
# See COPYING for license details.

# $Id: __init__.py 51 2006-09-23 14:06:13Z filipw $

"""
Discrete forward and inverse wavelet transform, stationary wavelet transform,
wavelet packets signal decomposition and reconstruction module.
"""

from _pywt import *
from wnames import *
from multilevel import *
from multidim import *
from wavelet_packets import WaveletPacket
import tresholding

from release_details import version as __version__, author as __author__, license as __license__
__all__ = []
__all__ += _pywt.__all__
__all__ += wnames.__all__
__all__ += wavelet_packets.__all__
__all__ += multilevel.__all__
__all__ += multidim.__all__
__all__ += ['__version__', '__author__']
          
#del _pywt
del wnames, multilevel, multidim, wavelet_packets
