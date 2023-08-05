#!/usr/bin/env python

from distutils.core import setup
from distutils.extension import Extension
import glob, os, os.path

version = "0.1.2" # open("version.txt", 'r').read().strip()

long_description = \
"""PyWavelets is a Python module that can perform discrete forward and
inverse wavelet transform, stationary wavelet transform and wavelet
packets signal decomposition and reconstruction.
"""

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: C',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules'
]

if os.path.exists('MANIFEST'): os.remove('MANIFEST')

try:
    from Pyrex.Distutils import build_ext
    has_pyrex = True
except ImportError:
    has_pyrex = False

if has_pyrex:
    pyx_sources = ['src/_pywt.pyx']
    cmdclass    = {'build_ext': build_ext}
else:
    pyx_sources = ['src/_pywt.c']
    cmdclass    = {}

ext_modules=[ 
    Extension("pywt._pywt",
        sources = pyx_sources + ["src/convolution.c", "src/wavelets.c", "src/wt.c"], 
        include_dirs = ['src'],
        library_dirs = [],
        runtime_library_dirs = [],
        libraries = [],
        extra_compile_args=[], #["-O3"],
    extra_link_args = [],
    export_symbols = [],
    #language = "pyrex",
    ),
]

setup(
    name = 'PyWavelets',
    version = version,
    description = "PyWavelets, wavelet transform module.",
    long_description = long_description,
    author = 'Filip Wasilewski',
    author_email = 'filipwasilewski@gmail.com', 
    url = 'http://www.pybytes.com/pywavelets/',
    download_url = "",
    license = 'MIT',
    ext_modules=ext_modules,
    platforms = ["any"],
    packages = ['pywt'],
    package_dir = {'pywt':'pywt'},
    #script_args = ["build_ext"],
    classifiers = classifiers,
    cmdclass = cmdclass
)
