#simple module to show the ploting of random data

import pycuda.gpuarray as cuda
from matplotlib.pylab import *

size = 1000

#random data generated on gpu
a = cuda.array(size).randn()


subplot(211)
plot(a)
grid(True)
ylabel('plot - gpu')

subplot(212)
hist(a, 100)
grid(True)
ylabel('histogram - gpu')

#and save it
savefig('plot-random-data')