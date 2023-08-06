import gtk
from pylab import setp, arange, array

class Rhythm_path:
    """ Add rhythm path to the canvas """
    def __init__(self, canvas, i=0, band=0.5):
        self.x = []   # x of the skeleton line
        self.y = []   # y of the skeleton line
        self.v = []   # indices of the eds
        self.px = []  # xpoints in path
        self.py = []  # ypoints in path
        self.pu = []  # y points for the upper boundary
        self.pl = []  # y points for the lower boundary
        #---------------------------------
        self.band = band      # Frequency band (herz)
        self.plhndl = []     # Plot handle
        #---------------------------------
        self.canvas = canvas
        self.id = i
        self.butcb = [None,None,None] # Buttons callbacks
        self.box = gtk.HBox(False,0)
        self.b_adj = gtk.Adjustment(value=band,\
                lower=0.0,\
                upper=1000,\
                step_incr=0.01,\
                page_incr=0.04)
        band_spin = gtk.SpinButton(self.b_adj,climb_rate=0.2,digits=3)
        band_spin.set_numeric(True)
        band_spin.connect('value-changed',self.cb_band)
        self.buts = [gtk.ToggleButton('%d' %int(i)),\
                gtk.CheckButton('P'), gtk.CheckButton('R'),\
                band_spin]
        for b in self.buts:
            self.box.pack_start(b,False,False,0)

    def __del__(self):
        print 'Destructor of RhythmPath'
        for b in self.buts:
            self.box.remove(b)
        self.clear()
        self.rclear()
        for i in xrange(4):
            setp(self.plhndl[i], 'data', (self.px, self.py), 'visible', False)
        self.canvas.draw()
        pass

    def append(self,x,y):
        """ Append a point to a rhythm"""
        if len(self.px) == 0 or x > self.px[-1]:
            self.px.append(x)
            self.py.append(y)
            self.pu.append(y+self.band)
            self.pl.append(y-self.band)
        else:
            k = arange(len(self.px))
            i = min(k[array(self.px) > x])
            self.px.insert(i,x)
            self.py.insert(i,y)
            self.pu.insert(i,y+self.band)
            self.pl.insert(i,y-self.band)

    def recalc_ul(self):
        for i in range(len(self.py)):
            self.pu[i] = self.py[i] + self.band 
            self.pl[i] = self.py[i] - self.band 

    def pop(self):
        self.px.pop()
        self.py.pop()
        self.pu.pop()
        self.pl.pop()

    def clear(self):
        while len(self.px) > 0:
            self.pop()
    
    def rclear(self):
        """ Rhythm clear """
        while len(self.x) > 0:
            self.x.pop()
            self.y.pop()
            self.v.pop()

    def plot_setup(self,ax,L):
        self.plhndl.append(ax.plot(self.px,self.py,'or-'))
        self.plhndl.append(ax.plot(self.px,array(self.py)+self.band,'y-'))
        self.plhndl.append(ax.plot(self.px,array(self.py)-self.band,'y-'))
        self.plhndl.append(ax.plot(self.x, self.y,'-',color='w',linewidth=5.0, alpha=0.5))
        setp(ax,'xlim',L[0], 'ylim',L[1])

    def preplot(self,canvas,vis=True):
        setp(self.plhndl[0],'data', (self.px,self.py),'visible',vis)
        setp(self.plhndl[1],'data', (self.px,array(self.py)+self.band),'visible',vis)
        setp(self.plhndl[2],'data', (self.px,array(self.py)-self.band),'visible',vis)
        canvas.draw()

    def cb_band(self,w,data=0):
        """Callback for changing the frequency band for rhythm selection"""
        self.band = w.get_value()
        self.recalc_ul()
        self.preplot(self.canvas)

    def rreplot(self,canvas,vis=True):
        setp(self.plhndl[3],'data', (self.x,self.y),'visible',vis)
        canvas.draw()


