# General purpose utilities

from pylab import *

def log2(x):
    """Base 2 logarithm"""
    return log(x)/log(2.)

def make_progress_str(i,L=100):
    """Make a progress string with a rotating stick"""
    return '\r%3d%s %s' % (100*i/L, '%', ('|','/','-','\\')[i%4])


def deriv(x,y):
    """Calculate derivative of a signal"""
    return  .5*((y[1:-1] - y[0:-2]) / (x[1:-1] - x[0:-2]) + \
            (y[2:]   - y[1:-1]) / (x[2:]   - x[1:-1]))

def get_extr_deriv(x,y,maxf=True,wth=4):
    """Derivative-based extrema detection"""
    der = deriv(x,y)
    a = der > 0
    if maxf:
        a = a[1:] < a[:-1]
    else:
        a = a[1:] > a[:-1]

    k = arange(len(a))[a]
    xe = ones(len(k),dtype='d')
    ye = ones(len(k),dtype='d')

    for j,i in enumerate(k):
        p = polyfit(x[i+1:i+3], der[i:i+2], 1)
        xe[j] = -p[1] / p[0] #???
        p = polyfit(x[i:i+3], y[i:i+3], 2)
        #ye[j] = polyval(p, x[i+1:i+2])[0]
        ye[j] = polyval(p, (xe[j],) )[0]
    return xe,ye

def detrend1(vect, n=1):
    j = arange(len(vect))
    return vect - polyval(polyfit(j, vect, n), j)

def deoutburst(vect, n = 4):
    d = std(vect)
    m = mean(vect)

    low = m - n*d
    high = m+ n*d

    res = vect.copy()
    for i in xrange(len(vect)):
        if vect[i] < low:
            res[i] = low
        elif vect[i] > high:
            res[i] = high
        else:
            res[i] = vect[i]
    return res

