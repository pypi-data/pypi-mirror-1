"""
Unit tests for the NeuroTools.analysis module
"""

from NeuroTools import analysis
import numpy, unittest
from numpy import pi, sin

# test simple_frequency_spectrum


class AnalysisTest(unittest.TestCase):

    def testSimpleFrequencySpectrum(self):
        
        ph = [0.5*pi, 1.2*pi, 0.3*pi]
        x = lambda A, ph, f, t: A[0] + A[1]*sin(2*pi*f/1000.0*t + ph[0]) + A[2]*sin(2*pi*2*f/1000.0*t + ph[1]) + A[3]*sin(2*pi*3*f/1000.0*t + ph[2])
        durations = [10.0, 10.0, 30.0]
        binwidths = [1.0, 5.0, 10.0]
        
        for i in range(10):
            A = numpy.random.uniform(-10, 10, size=4)
            #print A
            for f in 0.5, 1.0, 2.0, 10.0, 99.0: # cycles/sec
                for duration, binwidth in zip(durations, binwidths):
                    if 3*f < 1000.0/binwidth: # binwidth limits the max frequency
                        X = x(A, ph, f, numpy.arange(0, duration*1000.0, binwidth))
                        spect = analysis.simple_frequency_spectrum(X)
                        samples = numpy.array([0, 1, 2, 3])*int(f*duration)
                        components = spect[samples]
                        #print f, duration, binwidth, components
                        assert numpy.all(abs(abs(A) - components) < 1e-13), abs(A)-components

    def testCCF(self):
        a=numpy.arange(1000)
        z=analysis.ccf(a,a)
        assert z[len(z)/2] == 1

if __name__ == "__main__":
    unittest.main()