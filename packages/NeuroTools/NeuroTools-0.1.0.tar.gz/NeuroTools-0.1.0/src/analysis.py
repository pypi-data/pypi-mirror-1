# -*- coding: utf8 -*-
"""
NeuroTools.analysis
==================

A collection of analysis functions that may be used by NeuroTools.signals or other packages.

Classes
-------

TuningCurve - A tuning curve object (not very documented)


Functions
---------

ccf                       - fast cross correlation function based on fft
simple_frequency_spectrum - Simple frequencxy spectrum
arrays_almost_equal       - comparison of two arrays
"""

import os, numpy
from NeuroTools import check_dependency


def arrays_almost_equal(a, b, threshold):
    return (abs(a-b) < threshold).all()

def ccf(x, y, axis=None):
    """
    Computes the cross-correlation function of two series x and y.
    Note that the computations are performed on anomalies (deviations from
    average).
    Returns the values of the cross-correlation at different lags.
        
    Inputs:
        x    - 1D MaskedArray of a Time series.
        y    - 1D MaskedArray of a Time series.
        axis - integer *[None]* Axis along which to compute (0 for rows, 1 for cols).
               If `None`, the array is flattened first.
    
    Examples:
        >> z= arange(1000)
        >> ccf(z,z)

    """
    assert(x.ndim == y.ndim, "Inconsistent shape !")
#    assert(x.shape == y.shape, "Inconsistent shape !")
    if axis is None:
        if x.ndim > 1:
            x = x.ravel()
            y = y.ravel()
        npad = x.size + y.size
        xanom = (x - x.mean(axis=None))
        yanom = (y - y.mean(axis=None))
        Fx = numpy.fft.fft(xanom, npad, )
        Fy = numpy.fft.fft(yanom, npad, )
        iFxy = numpy.fft.ifft(Fx.conj()*Fy).real
        varxy = numpy.sqrt(numpy.inner(xanom,xanom) * numpy.inner(yanom,yanom))
    else:
        npad = x.shape[axis] + y.shape[axis]
        if axis == 1:
            if x.shape[0] != y.shape[0]:
                raise ValueError, "Arrays should have the same length!"
            xanom = (x - x.mean(axis=1)[:,None])
            yanom = (y - y.mean(axis=1)[:,None])
            varxy = numpy.sqrt((xanom*xanom).sum(1) * (yanom*yanom).sum(1))[:,None]
        else:
            if x.shape[1] != y.shape[1]:
                raise ValueError, "Arrays should have the same width!"
            xanom = (x - x.mean(axis=0))
            yanom = (y - y.mean(axis=0))
            varxy = numpy.sqrt((xanom*xanom).sum(0) * (yanom*yanom).sum(0))
        Fx = numpy.fft.fft(xanom, npad, axis=axis)
        Fy = numpy.fft.fft(yanom, npad, axis=axis)
        iFxy = numpy.fft.ifft(Fx.conj()*Fy,n=npad,axis=axis).real
    # We juste turn the lags into correct positions:
    iFxy = numpy.concatenate((iFxy[len(iFxy)/2:len(iFxy)],iFxy[0:len(iFxy)/2]))
    return iFxy/varxy


def _dict_max(D):
    """
    For a dict containing numerical values, contain the key for the
    highest value. If there is more than one item with the same highest
    value, return one of them (arbitrary - depends on the order produced
    by the iterator).
    """
    max_val = max(D.values())
    for k in D:
        if D[k] == max_val:
            return k
        
def simple_frequency_spectrum(x):
    """
    Very simple calculation of frequency spectrum with no detrending,
    windowing, etc. Just the first half (positive frequency components) of
    abs(fft(x))
    """
    spec = numpy.absolute(numpy.fft.fft(x))
    spec = spec[:len(x)/2] # take positive frequency components
    spec /= len(x)         # normalize
    spec *= 2.0            # to get amplitudes of sine components, need to multiply by 2
    spec[0] /= 2.0         # except for the dc component
    return spec

class TuningCurve(object):
    """Class to facilitate working with tuning curves."""

    def __init__(self, D=None):
        """
        If `D` is a dict, it is used to give initial values to the tuning curve.
        """
        self._tuning_curves = {}
        self._counts = {}
        if D is not None:
            for k,v in D.items():
                self._tuning_curves[k] = [v]
                self._counts[k] = 1
                self.n = 1
        else:
            self.n = 0

    def add(self, D):
        for k,v  in D.items():
            self._tuning_curves[k].append(v)
            self._counts[k] += 1
        self.n += 1

    def __getitem__(self, i):
        D = {}
        for k,v in self._tuning_curves[k].items():
            D[k] = v[i]
        return D
    
    def __repr__(self):
        return "TuningCurve: %s" % self._tuning_curves

    def stats(self):
        """Return the mean tuning curve with stderrs."""
        mean = {}
        stderr = {}
        n = self.n
        for k in self._tuning_curves.keys():
            arr = numpy.array(self._tuning_curves[k])
            mean[k] = arr.mean()
            stderr[k] = arr.std()*n/(n-1)/numpy.sqrt(n)
        return mean, stderr

    def max(self):
        """Return the key of the max value and the max value."""
        k = _dict_max(self._tuning_curves)
        return k, self._tuning_curves[k]