#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
benchmark_linear.py
=========================

Having fixed the background noise we are just studying now how different
signal to noise ratios are integrated by the neurons.

Laurent Perrinet, INCM, CNRS

$ Id $

"""

import os, sys, numpy, pylab, shelve


name = sys.argv[0].split('.')[0] # name of the current script withpout the '.py' part
results = shelve.open('results/mat-' + name)
try:

    temporal_ON = results['temporal_ON']
    temporal_OFF = results['temporal_OFF']
    lower_edges = results['lower_edges']
    params = results['params']
    #if (params == retina.params): raise('Parameters have changed')

except:
    N, N_exp = 1000, 6
    t_smooth = 100. # width (in ms) of the integration window
    from retina import *
    retina = Retina(N)
    retina.params['amplitude'] = numpy.ones(retina.params['amplitude'].shape)
    snr  = retina.params['snr']* numpy.linspace(0.1,2.0,N_exp)
    from NeuroTools.parameters import ParameterSpace
    p = ParameterSpace({'snr' : ParameterRange(list(snr))})

    # calculates the dimension of the parameter space
    results_dim, results_label = p.parameter_space_dimension_labels()

    # creates results array with size of parameter space dimension
    data = retina.run(retina.params,verbose=False)
    lower_edges = data['out_ON_DATA'].time_axis(t_smooth)
    N_smooth = len(lower_edges)
    
    temporal_ON, temporal_OFF = [],[]
    import progressbar # see http://projects.scipy.org/pipermail/scipy-dev/2008-January/008200.html
    pbar=progressbar.ProgressBar(widgets=[name, " ", progressbar.Percentage(), ' ',
            progressbar.Bar(), ' ', progressbar.ETA()], maxval=N_exp)
    for i_exp,experiment in enumerate(p.iter_inner()):
        params = retina.params
        params.update(experiment) # updates what changed in the dictionary
        # simulate the experiment and get its data
        data = retina.run(params,verbose=False)
        # calculating the index in the parameter space
        index = p.parameter_space_index(experiment)
        # put the data at the right position in the results array
        temporal_ON.append(sum(data['out_ON_DATA'].firing_rate(t_smooth))/N)#
        temporal_OFF.append(sum(data['out_OFF_DATA'].firing_rate(t_smooth))/N)#
        pbar.update(i_exp)

    
    results['lower_edges'] = lower_edges
    results['temporal_ON'] = temporal_ON
    results['temporal_OFF'] = temporal_OFF
    results['params'] = params

    pbar.finish()

results.close()

###############################################################################

from NeuroTools.plotting import pylab_params

""" Figure 1

Prints to a figure the mean firing rate for the output (ON and OFF) as a function
of the different parameter values. It's similar to a CRF function.

"""
#pylab.close('all')
#pylab.rcParams.update(pylab_params(fig_width_pt = 497.9/2., ratio = 1.))
pylab.figure(1)
fmax = numpy.max([numpy.max(temporal_OFF[:]),numpy.max(temporal_ON[:])])

pylab.subplot(211)
for i_exp in range(N_exp):
    pylab.plot(lower_edges[:-1] + t_smooth/2,  # TODO add a half bin
                    temporal_ON[i_exp])#
pylab.xticks( numpy.round(numpy.linspace(0, retina.params.simtime, 5),0) )
pylab.ylabel('ON Firing frequency (Hz/neuron)')
pylab.axis([0, retina.params.simtime, 0.0, fmax])
pylab.subplot(212)
for i_exp in range(N_exp):
    pylab.plot(lower_edges[:-1] + t_smooth/2,  # TODO add a half bin
                    temporal_OFF[i_exp],
                        label= 'snr= %5.3f' % p.snr._values[i_exp] )
pylab.xticks( numpy.round(numpy.linspace(0, retina.params.simtime, 5),0) )
pylab.ylabel('OFF Firing frequency (Hz/neuron)')
pylab.xlabel('time (ms)')
pylab.axis([0, retina.params.simtime, 0.0, fmax ])

pylab.legend(loc='upper right')


if 0:
    pylab.ion()
    #pylab.show()
else:
    pylab.savefig('results/fig-' + name + '.pdf')
    pylab.savefig('results/fig-' + name + '.png', dpi = 300)

