# Continuous wavelet transfrom via Fourier transform
# Collection of routines for wavelet transform via FFT algorithm


#-- Some naming and other conventions --
# use f instead of omega wherever rational/possible
# *_ft means Fourier transform

#-- Some references --
# [1] Mallat, S.  A wavelet tour of signal processing
# [2] Addison, Paul S. The illustrated wavelet transform handbook
# [3] Torrence and Compo. A practical guide to wavelet
#     analysis. Bulletin of American Meteorological Society. 1998, 79(1):61-78

import numpy
from numpy.fft import fft, ifft, fftfreq

#try:
#    from scipy.special import gamma
#except:



pi = numpy.pi

class DOG:
    """Derivative of Gaussian, general form"""
    # Incomplete, as the general form of the mother wavelet
    # would require symbolic differentiation.
    # Should be enough for the CWT computation, though

    def __init__(self, m = 1.):
        self.order = m
        self.fc = (m+.5)**.5 / (2*pi)
    
    def psi_ft(self, f):
        c = 1j**self.order / numpy.sqrt(gamma(self.order + .5)) #normalization
        w = 2*pi*f
        return c * w**self.order * numpy.exp(-.5*w**2)

class Mexican_hat:
    def __init__(self, sigma = 1.0):
        self.sigma = sigma
        self.fc = .5 * 2.5**.5 / pi
    def psi_ft(self, f):
        """Fourier transform of the Mexican hat wavelet"""
        c = numpy.sqrt(8./3.) * pi**.25 * self.sigma**2.5 
        wsq = (2. * pi * f)**2.
        return -c * wsq * numpy.exp(-.5 * wsq * self.sigma**2.)
    def psi(self, tau):
        """Mexian hat wavelet as described in [1]"""
        xsq = (tau / self.sigma)**2.
        c = 2 * pi**-.25 / numpy.sqrt(3 * self.sigma) # normalization constant from [1]
        return c * (1 - xsq) * numpy.exp(-.5 * xsq)
    def cone(self, f):
        "e-folding time [Torrence&Compo]. For frequencies"
        return self.f0*2.0**0.5 / f
    def cone_s(self, s):
        "e-folding time [Torrence&Compo]. For scales"
        return 2.**0.5*s
    def set_f0(self, f0):
        pass

def heavyside(x):
    return 1.0*(x>0.0)

class Morlet:
    def __init__(self, f0 = 1.5):
        self.set_f0(f0)
    def psi(self, t):
        pi**0.25 * exp(-t**2 / 2.) * exp(2j*pi*self.fc*t) #[3]
    def psi_ft(self, f):
        """Fourier transform of the approximate Morlet wavelet
            f0 should be more than 0.8 for this function to be
            correct."""
        # [3]
        coef = (pi**-.25) * heavyside(f)
        return  coef * numpy.exp(-.5 * (2. * pi * (f - self.fc))**2.)
    def cone(self, f):
        "e-folding time [Torrence&Compo]. For frequencies"
        return self.f0*2.0**0.5 / f
    def cone_s(self, s):
        "e-folding time [Torrence&Compo]. For scales"
        return 2.**0.5*s
    def set_f0(self, f0):
        self.f0 = f0
        self.fc = f0


def next_pow2(x):
    return 2.**numpy.ceil(numpy.log2(x))

def pad_func(ppd):
    func = None
    if ppd == 'zpd':
        func = lambda x,a:  x*0.0
    elif ppd == 'cpd':
        func = lambda x,a:  x*a
    return func
    
def evenp(n):
    return not n%2

def cwt_a(signal, scales, sampling_scale = 1.0,
          wavelet=Mexican_hat(),
          ppd = 'zpd'):
    """ Continuous wavelet transform via fft. Scales version."""

    siglen = len(signal)

    if not evenp(siglen) :
        siglen -= 1
        signal = signal[:-1]

    needpad = wavelet.cone_s(numpy.max(scales))
    ftlen = int(next_pow2(siglen + 2*needpad))
    padlen = int((ftlen - siglen)/2)



    padseq  = numpy.ones((padlen,))
    padfunc = pad_func(ppd)


    padded_signal = numpy.concatenate((padfunc(padseq, signal[0]),
                                       signal,
                                       padfunc(padseq, signal[-1])))

    signal_ft = fft(padded_signal)     # FFT of the signal

    ## create the result matrix beforehand
    W = numpy.zeros((len(scales), siglen), 'complex')

    ftfreqs = fftfreq(ftlen, sampling_scale)  # FFT frequencies

    # Now fill in the matrix
    for n,s in enumerate(scales):
        psi_ft_bar = numpy.conjugate(wavelet.psi_ft(s * ftfreqs))
        psi_ft_bar *= (2*pi*s/sampling_scale)**0.5 # Normalization from [3]
        #W[n,:] = (s**.5) * ifft(signal_ft * psi_ft_bar)
        x = ifft(signal_ft * psi_ft_bar)
        
        W[n,:] = x[padlen:-padlen]
    return W


def cwt_f(signal, freqs, Fs=1.0, wavelet = Morlet(), ppd = 'zpd'):
    """Continuous wavelet transform -- frequencies version"""
    scales = wavelet.fc/freqs
    dt = 1./Fs
    return cwt_a(signal, scales, dt, wavelet, ppd)


def eds(x, f0=1.5):
    "Energy density surface [2,3]"
    ## Update, simulations with MK (as in [3]) suggest that I
    ## shouldn't divide by f0 to obtain correct normalisation,
    ## e.g. 1 s.d. in mean for white noise signal
    #return abs(x)**2/f0
    return abs(x)**2


def xwt_f(sig1, sig2, freqs, Fs=1.0, wavelet=Morlet()):
    "Cross-wavelet coeficients for 2 signals"
    cwtf = lambda x: cwt_f(x, freqs, Fs, wavelet)
    return xwt(cwtf(sig1),cwtf(sig2))

def absxwt_f(sig1, sig2, freqs, Fs=1.0, wavelet=Morlet()):
    "Cross-wavelet power for 2 signals"
    return abs(xwt_f(sig1,sig2, freqs, Fs, wavelet))/wavelet.f0**0.5

def absxwt_a(sig1, sig2, scales, dt=1.0, wavelet=Morlet()):
    "Cross-wavelet power for 2 signals"
    return abs(xwt_f(sig1,sig2, freqs, Fs, wavelet))/wavelet.f0**0.5


def xwt(wcoefs1,wcoefs2):
    "Cross wavelet transform for 2 sets of coefficients"
    return wcoefs1*wcoefs2.conjugate()

def absxwt(wcoefs1,wcoefs2, f0=1.5):
    "Cross-wavelet power for 2 sets of coefficients"
    ## Why do I divide by f_0^2 here?
    return  abs(xwt(wcoefs1,wcoefs2))/f0**0.5

def wtc_a(sig1, sig2, scales, dt=1.0, wavelet=Morlet()):
    cwta = lambda x: cwt_a(x, scales, dt, wavelet)
    return coherence_a(cwta(sig1), cwta(sig2), scales, dt, wavelet)


def wtc_f(sig1, sig2, freqs, Fs=1.0, wavelet=Morlet()):
    cwtf = lambda x: cwt_f(x, freqs, Fs, wavelet)
    return coherence_f(cwtf(sig1), cwtf(sig2), freqs, Fs, wavelet.f0)

def coherence_a(x,y,scales,dt,f0=1.5):
    # almost not useful 
    #scor =numpy.ones(x.shape[1])[:,numpy.newaxis] * scales
    #scor = numpy.transpose(scor)
    sx = wsmooth_a(abs(x)**2,scales,dt)
    sy= wsmooth_a(abs(y)**2,scales,dt)
    sxy = wsmooth_a((x*y.conjugate()), scales, dt)
    return abs(sxy)**2/(sx.real*sy.real)

def coherence_f(x,y,freqs, Fs=1.0, f0=1.5):
    return coherence_a(x,y,f0/freqs, 1.0/Fs, f0)

def cphase(x,y):
    #hard to interprete :(
    d = xwt(x,y)
    return numpy.arctan2(d.imag, d.real)

def cwt_phase(x):
    return numpy.arctan2(x.imag, x.real)


def wsmooth_a(coefs, scales, dt = 1.0, wavelet=Morlet()):
    "Smoothing of wavelet coefs. Scales version"
    #G = lambda omega,s: numpy.exp(-0.5 * s**2.0 *omega**2.0) # Literature
    G = lambda omega,s: numpy.exp(-0.25 * s**2.0 *omega**2.0) 

    W = numpy.zeros(coefs.shape, 'complex')
    fftom = 2*pi*fftfreq(coefs.shape[1], dt) 

    for n,s in enumerate(scales):
        W[n,:] = ifft(fft(coefs[n,:]) * G(fftom, s/dt))

    # TODO: scale smoothing
    return W


