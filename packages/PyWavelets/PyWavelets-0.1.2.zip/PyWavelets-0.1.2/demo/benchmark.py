#!/usr/bin/env python

import pywt
import array
from time import clock
import pylab
import gc, sys
sys.stderr = sys.stdout
#gc.set_debug(gc.DEBUG_LEAK)

using_numpy = pywt.use_numpy(1)
if using_numpy:
    import numpy
    print "Using numpy module"

sizes = (100, 120, 150, 200, 250, 300, 500, 750,
         1000, 2000, 3000, 5000, 7500,
         10000, 20000, 30000, 50000, 75000,
         100000, 200000, 300000, 500000, 750000,
         1000000, 2000000, 5000000, 10000000) # len = 25

#sizes = sizes[:20]

wavelet_names = ['db1', 'db2', 'db4', 'sym5', 'sym10']
wavelets = [pywt.Wavelet(n) for n in wavelet_names]
mode = pywt.MODES.zpd

times_dwt = [[] for i in range(len(wavelets))]
times_idwt = [[] for i in range(len(wavelets))]

repeat = 3

for j, size in enumerate(sizes):
    if size > 500000:
        print "Warning, too big data size may cause page swapping if computer does not have enough memory."

    if using_numpy:
        data = numpy.ones((size,), numpy.Float64)
    else:
        data = array.array('d', [1.0]) * size
    print ("%d/%d" % (j+1, len(sizes))).rjust(6), str(size).rjust(9),
    for i, w in enumerate(wavelets):
        min_t1, min_t2 = 9999., 9999.
        for _ in xrange(repeat):
            t1 = clock()
            (a,d) = pywt.dwt(data, w, mode)
            t1 = clock() - t1
            min_t1 = min(t1, min_t1)

            t2 = clock()
            a0 = pywt.idwt(a, d, w, mode)
            t2 = clock() - t2
            min_t2 = min(t2, min_t2)
            
        times_dwt[i].append(min_t1)
        times_idwt[i].append(min_t2)
        print '.',
    gc.collect()
    print


for j, (times,name) in enumerate([(times_dwt, 'dwt'), (times_idwt, 'idwt')]):
    pylab.figure(j)
    pylab.title(name)
    for i, n in enumerate(wavelet_names):
        pylab.loglog(sizes, times[i], label=n)

    pylab.legend(loc='best')
    pylab.xlabel('len(x)')
    pylab.ylabel('time [s]')

pylab.show()
