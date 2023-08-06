# Colormaps for Swan

#from numpy import *
from pylab import *
import matplotlib


def hsv2rgb(ctuple):
    """Convert hsv tuple to rgb tuple
    based on wikipedia page"""
    h,s,v = ctuple
    Hi = mod(floor(h/60.), 6)
    f = h/60. - floor(h/60.)
    p = v*(1 - s)
    q = v*(1 - s*f)
    t = v*(1 - (1-f)*s)
    
    if (Hi == 0): r,g,b = v,t,p
    elif (Hi == 1): r,g,b = q,v,p
    elif (Hi == 2): r,g,b = p,v,t
    elif (Hi == 3): r,g,b = p,q,v
    elif (Hi == 4): r,g,b = t,p,v
    elif (Hi == 5): r,g,b = v,p,q
    
    return r,g,b

def get_rgbswan_data1():
    return {'red':   ((0, 0, 0), 
                      (0.2, .1, .1),
                      (0.4, .4, .4),
                      (0.6, .6, .6),
                      (0.8, 1, 1),
                      (1, 1, 1)),
            'green': ((0., 0, 0), 
                      (0.2, 0.5, 0.5), 
                      (0.4, 1, 1),
                      (0.6, .8, .8),
                      (0.8, 0.9, 0.9),
                      (1, 0.2, 0.2)),
            'blue':  ((0, 1, 1), 
                      (0.2, 0.6, 0.6), 
                      (0.4, 0.3, 0.3),
                      (0.6, 0, 0),
                      (0.8, 0, 0),
                      (1.0, 0, 0))}

def get_rgbswan_data2():
    sat,val = 0.9,0.95
    colors = {'red':0,'green':1,'blue':2}
    step = 0.05

    rgb_vect = [ (x, hsv2rgb(((1-x)*220, sat, val))) 
                 for x in arange(0,1 + step,step)]
    res = {}

    for color,ind in colors.items():
        res[color] = [(x[0], x[1][ind], x[1][ind]) for x in rgb_vect]    
    return res

def set_rgbswan_cm():
    LUTSIZE = mpl.rcParams['image.lut']
    
    _rgbswan_data =  get_rgbswan_data2() 

    cm.datad['rgbswan'] = _rgbswan_data
    cm.rgbswan  = matplotlib.colors.LinearSegmentedColormap('rgbswan',
                                                            _rgbswan_data, LUTSIZE)
    return cm.rgbswan



def rgbswan():
    '''
    set the default colormap to jet and apply to current image if any.
    See help(colormaps) for more information
    '''
    rc('image', cmap='rgbswan')
    im = gci()

    if im is not None:
        im.set_cmap(cm.rgbswan)
    draw_if_interactive()
