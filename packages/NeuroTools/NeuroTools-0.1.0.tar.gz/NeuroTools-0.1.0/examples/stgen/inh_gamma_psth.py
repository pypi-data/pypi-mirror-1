# Generate the PSTH for an inhomogeneous gamma renewal process
# with a step change in the rate (b changes, a stays fixed)



import numpy
from NeuroTools import stgen

dt = 10.0
t = numpy.arange(0,1000.0,dt) 
rate = numpy.ones_like(t)*20.0

# stepup

i_start = t.searchsorted(400.0,'right')-1
i_end = t.searchsorted(600.0,'right')-1

rate[i_start:i_end] = 40.0

a = numpy.ones_like(t)*3.0
b = numpy.ones_like(t)/a/rate

psth = zeros_like(t)

stg = stgen.StGen()

for i in xrange(10000):
    st = stg.inh_gamma_generator(a,b,t,1000.0,array=True)
    psth+=numpy.histogram(st,t)[0]

# normalize

psth = psth.astype(float)
psth/= dt*10000.0/1000.0

plot(t,psth,linestyle='steps')

