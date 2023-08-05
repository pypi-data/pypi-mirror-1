import wx
from params import params
from wx import xrc
import wxvideo
import imagesk
import scipy.signal as signal
import scipy.ndimage as ndimage
import numpy as num
import houghcircles
from houghcircles import *
import scipy.misc.pilutil as pilutil
import pkg_resources # part of setuptools
import colormapk

RSRC_FILE = pkg_resources.resource_filename( __name__, "setarena.xrc" )
RESIZE = 500
NTHRESHSTEPS = 30
DCLICK = 8

class SetArena:

    def __init__(self,parent,bg):

        self.parent = parent
        self.im = bg.copy()
        rsrc = xrc.XmlResource(RSRC_FILE )
        self.frame = rsrc.LoadFrame(parent,"detect_arena_frame")

        self.InitControlHandles()
        self.InitializeValues()
        self.BindCallbacks()
        self.OnResize()
        self.ShowImage()

    def DoDraw( self ):
        """Draw image to window."""

        self.img_wind.Refresh( eraseBackground=False )

    def control(self,ctrlname):
        return xrc.XRCCTRL(self.frame,ctrlname)

    def InitControlHandles(self):

        self.edge_threshold_button = self.control('edge_threshold_button')
        self.detect_button = self.control('detect_button')
        self.refine_button = self.control('refine_button')
        self.done_button = self.control('done_button')
        self.img_panel = self.control('img_panel')
        box = wx.BoxSizer( wx.VERTICAL )
        self.img_panel.SetSizer( box )
        self.img_wind = wxvideo.DynamicImageCanvas( self.img_panel, -1 )
        box.Add( self.img_wind, 1, wx.EXPAND )
        self.img_panel.SetAutoLayout( True )
        self.img_panel.Layout()
        self.directions_text = self.control('directions_text')

    def InitializeValues(self):

        wx.BeginBusyCursor()
        wx.Yield()

        # resize the image for speed
        nr0 = self.im.shape[0]
        nc0 = self.im.shape[1]
        if RESIZE > min(nr0,nc0):
            self.nc_resize_ratio = 1.
            self.nr_resize_ratio = 1.
            nc = nc0
            nr = nr0
        else:
            if nr0 < nc0:
                nc = nc0*RESIZE/nr0
                nr = RESIZE
                # multiply by nc_resize_ratio to go from real coordinates to smaller, resized
                # coordinates
                self.nc_resize_ratio = float(nc)/float(nc0)
                self.nr_resize_ratio = float(nr)/float(nr0)
            else:
                nr = nr0*RESIZE/nc0
                nc = RESIZE
                self.nc_resize_ratio = float(nc)/float(nc0)
                self.nr_resize_ratio = float(nr)/float(nr0)
            self.im = pilutil.imresize(self.im,[nr,nc])
        if params.arena_center_x is None:
            self.arena_center_x = .5*nc
        else:
            self.arena_center_x = params.arena_center_x * self.nc_resize_ratio
        if params.arena_center_y is None:
            self.arena_center_y = .5*nr
        else:
            self.arena_center_y = params.arena_center_y * self.nr_resize_ratio
        if params.arena_radius is None:
            self.arena_radius = .375*min(nc,nr)
        else:
            self.arena_radius = params.arena_radius * .5 * (self.nr_resize_ratio + self.nc_resize_ratio)

        # compute the edge magnitude image
        self.edgemag = edge(self.im)

        # set bounds on the threshold
        self.minedgemag = num.min(self.edgemag)
        self.maxedgemag = num.max(self.edgemag)
        self.edge_threshold_button.SetRange(0,NTHRESHSTEPS-1)

        # initialize value for edge threshold
        if params.arena_edgethresh is None:
            params.arena_edgethresh = choose_edge_threshold(self.edgemag)

        params.arena_edgethresh = min(params.arena_edgethresh,self.maxedgemag)
        params.arena_edgethresh = max(params.arena_edgethresh,self.minedgemag)

        # set value of threshold displayed
        v = int(num.round((params.arena_edgethresh-self.minedgemag)/(self.maxedgemag-self.minedgemag)*NTHRESHSTEPS))
        self.edge_threshold_button.SetValue(v)

        # create the threshold image
        self.CreateEdgeImage()

        self.edgepoint = [self.arena_center_x + self.arena_radius,
                          self.arena_center_y]

        # set click mode
        self.selected_point = 'none'

        wx.EndBusyCursor()

    def BindCallbacks(self):

        # threshold button
        self.frame.Bind(wx.EVT_SPIN,self.ChangeThreshold,self.edge_threshold_button)
        # mode button
        self.frame.Bind(wx.EVT_BUTTON,self.Detect,self.detect_button)
        # enter button
        self.frame.Bind(wx.EVT_BUTTON,self.Refine,self.refine_button)

        # mouse click
        self.img_wind.Bind(wx.EVT_LEFT_DOWN,self.MouseDown)
        self.img_wind.Bind(wx.EVT_LEFT_UP,self.MouseUp)

    def ChangeThreshold(self,evt):

        if evt is None:
            return

        v = self.edge_threshold_button.GetValue()
        params.arena_edgethresh = float(v) / float(NTHRESHSTEPS) * (self.maxedgemag - self.minedgemag) + self.minedgemag
        self.CreateEdgeImage()
        wx.Yield()
        self.ShowImage()


    def Detect(self,evt=None):

        wx.BeginBusyCursor()
        wx.Yield()
        if self.edgepoint is None:
            theta = 0.
        else:
            theta = num.arctan2(self.edgepoint[1] - self.arena_center_y,self.edgepoint[0] - self.arena_center_x)
        [self.arena_center_x,self.arena_center_y,self.arena_radius] = \
                       detectarena(self.edgemag_zero)
        self.edgepoint[0] = self.arena_center_x + self.arena_radius*num.cos(theta)
        self.edgepoint[1] = self.arena_center_y + self.arena_radius*num.sin(theta)

        self.ShowImage()
        wx.EndBusyCursor()
        

    def Refine(self,evt=None):

        if self.arena_center_x is None:
            self.Detect(evt)
            return
        wx.BeginBusyCursor()
        wx.Yield()
        if self.edgepoint is None:
            theta = 0.
        else:
            theta = num.arctan2(self.edgepoint[1] - self.arena_center_y,self.edgepoint[0] - self.arena_center_x)
        [self.arena_center_x,self.arena_center_y,self.arena_radius] = \
                       detectarena(self.edgemag_zero,
                                   approxa=self.arena_center_x,
                                   approxb=self.arena_center_y,
                                   approxr=self.arena_radius)
        self.edgepoint[0] = self.arena_center_x + self.arena_radius*num.cos(theta)
        self.edgepoint[1] = self.arena_center_y + self.arena_radius*num.sin(theta)
        self.ShowImage()
        wx.EndBusyCursor()
        
    def CreateEdgeImage(self):

        self.edgemag_zero = self.edgemag.copy()
        self.edgemag_zero[self.edgemag < params.arena_edgethresh] = 0
        wx.Yield()
        self.image_shown = colormapk.colormap_image(self.edgemag_zero)

    def ShowImage(self):
        
        self.windowsize = [self.img_panel.GetRect().GetHeight(),
                           self.img_panel.GetRect().GetWidth()]
        (self.img_wind.bitmap,self.resize,self.img_size) = \
                   draw_circle(self.image_shown,self.arena_center_x,self.arena_center_y,
                               self.arena_radius,edgepoint=self.edgepoint,
                               windowsize=self.windowsize,thickness=3)
        wx.Yield()
        self.DoDraw()

    def OnResize(self,evt=None):

        if evt is not None: evt.Skip()
        self.frame.Layout()
        try:
            self.ShowImage()
        except AttributeError: pass # during initialization

    def MouseDown(self,evt):

        x = evt.GetX()/self.resize
        y = evt.GetY()/self.resize

        # compute distance to center
        dcenter = num.sqrt((x - self.arena_center_x)**2. + (y - self.arena_center_y)**2.)
        # compute distance to edgepoint
        dedge = num.sqrt((x - self.edgepoint[0])**2. + (y - self.edgepoint[1])**2.)
        mind = min(dcenter,dedge)
        if mind > DCLICK:
            return
        elif dcenter <= dedge:
            self.selected_point = 'center'
        else:
            self.selected_point = 'edge'

        wx.SetCursor(wx.StockCursor(wx.CURSOR_BULLSEYE))

    def MouseUp(self,evt):


        if self.selected_point == 'none':
            return

        wx.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))

        x = evt.GetX()
        y = evt.GetY()
        if (x > self.img_size[1]) or (y > self.img_size[0]):
            self.selected_point = 'none'
            return

        x /= self.resize
        y /= self.resize

        if self.selected_point == 'center':
            self.arena_center_x = x
            self.arena_center_y = y
        else:
            self.edgepoint[0] = x
            self.edgepoint[1] = y

        self.arena_radius = num.sqrt((self.edgepoint[0]-self.arena_center_x)**2.+(self.edgepoint[1]-self.arena_center_y)**2.)

        self.selected_point = 'none'
        self.ShowImage()

    def GetArenaParameters(self):
        x = self.arena_center_x / self.nc_resize_ratio
        y = self.arena_center_y / self.nr_resize_ratio
        r = self.arena_radius * 2. / (self.nc_resize_ratio + self.nr_resize_ratio)
        return [x,y,r]
        
def choose_edge_threshold(edgemag,FracPixelsNotEdges=.95):

    
    NPixelsNotEdges = FracPixelsNotEdges * edgemag.shape[0] * edgemag.shape[1]
    [counts,loweredges] = num.histogram(edgemag,100)
    idx, = num.where(counts.cumsum() > NPixelsNotEdges)
    idx = idx[0]+1
    if idx >= len(loweredges):
        idx = -1
    edgethresh = loweredges[idx]

    return edgethresh

def detectarena(edgemag,approxa=None,approxb=None,approxr=None):

    nr = edgemag.shape[0]
    nc = edgemag.shape[1]

    isguesseda = True
    isguessedb = True
    isguessedr = True
    if approxa is None:
        approxa = nc/2.
        isguesseda = False
    if approxb is None:
        approxb = nr/2.
        isguessedb = False
    if approxr is None:
        approxr = .375*min(nr,nc)
        isguessedr = False

    if isguesseda:
        mina = approxa - .025*nc
        maxa = approxa + .025*nc
    else:
        mina = approxa - .1*nc
        maxa = approxa + .1*nc
    if isguessedb:
        minb = approxb - .025*nr
        maxb = approxb + .025*nr
    else:
        minb = approxb - .1*nr
        maxb = approxb + .1*nr
    if isguessedr:
        minr = approxr - .025*min(nc,nr)
        maxr = approxr + .025*min(nc,nr)
    else:
        minr = approxr - .125*min(nc,nr)
        maxr = approxr + .125*min(nc,nr)
    
    nbinsa = 20
    nbinsb = 20
    nbinsr = 20
    peaksnhoodsize = num.array([1,1,1])
    
    binedgesa = num.linspace(mina,maxa,nbinsa+1)
    bincentersa = (binedgesa[:-1]+binedgesa[1:])/2.
    binedgesb = num.linspace(minb,maxb,nbinsb+1)
    bincentersb = (binedgesb[:-1]+binedgesb[1:])/2.
    binedgesr = num.linspace(minr,maxr,nbinsr+1)
    bincentersr = (binedgesr[:-1]+binedgesr[1:])/2.
    [x,y,r] = detectcircles(edgemag,binedgesa=binedgesa,
                            bincentersb=bincentersb,
                            bincentersr=bincentersr,
                            peaksnhoodsize=peaksnhoodsize,
                            peaksthreshold=0.,
                            maxncircles=1)


    t = num.linspace(0,2.*num.pi,200)
    
    # second pass
    binsizea = binedgesa[1] - binedgesa[0]
    mina = x - binsizea/2.
    maxa = x + binsizea/2.
    binsizeb = binedgesb[1] - binedgesb[0]
    minb = y - binsizeb/2.
    maxb = y + binsizeb/2.
    binsizer = binedgesr[1] - binedgesr[0]
    minr = r - binsizer/2.
    maxar= r + binsizer/2.

    binedgesa = num.linspace(mina,maxa,nbinsa+1)
    bincentersa = (binedgesa[:-1]+binedgesa[1:])/2.
    binedgesb = num.linspace(minb,maxb,nbinsb+1)
    bincentersb = (binedgesb[:-1]+binedgesb[1:])/2.
    binedgesr = num.linspace(minr,maxr,nbinsr+1)
    bincentersr = (binedgesr[:-1]+binedgesr[1:])/2.
    
    [x,y,r] = detectcircles(edgemag,binedgesa=binedgesa,
                            bincentersb=bincentersb,
                            bincentersr=bincentersr,
                            peaksnhoodsize=peaksnhoodsize,
                            peaksthreshold=0.,
                            maxncircles=1)
    
    return [x,y,r]

def sub2ind(sz,sub):

    nd = len(sub)
    ind = num.zeros(sub[0].shape,dtype='int')
    d = 1
    for i in range(nd-1,-1,-1):
        ind += sub[i]*d
        d *= sz[i]
    return ind

def houghcirclepeaks(h,numpeaks,threshold,nhood):

    # initialize the loop variables
    hnew = h
    nhood_center = (nhood-1)/2
    ia = num.array([],dtype='int')
    ib = num.array([],dtype='int')
    ir = num.array([],dtype='int')
    score = num.array([])

    while True:

        max_idx = num.argmax(hnew)
        (p,q,r) = ind2sub(hnew.shape,max_idx)

        if hnew[p,q,r] < threshold:
            break

        ia = num.append(ia,p)
        ib = num.append(ib,q)
        ir = num.append(ir,r)
        score = num.append(score,hnew[p,q,r])
        
        # suppress this maximum and its close neighbors
        p1 = p - nhood_center[0]
        p2 = p + nhood_center[0]
        q1 = q - nhood_center[1]
        q2 = q + nhood_center[1]
        r1 = r - nhood_center[2]
        r2 = r + nhood_center[2]
        
        # throw away out of bounds coordinates
        p1 = max(p1,0)
        p2 = min(p2,h.shape[0]-1)
        q1 = max(q1,0)
        q2 = min(q2,h.shape[1]-1)
        r1 = max(r1,0)
        r2 = min(r2,h.shape[2]-1)
        
        hnew[p1:p2,q1:q2,r1:r2] = 0

        if len(ir) == numpeaks:
            break

    return [ia,ib,ir,score]

#def houghcircles_wrapper(x,y,w,binedgesa,bincentersb,bincentersr):
#    npts = len(x)
#    nbinsa = len(binedgesa)-1
#    nbinsb = len(bincentersb)
#    nbinsr = len(bincentersr)
#
#    xx = new_doubleArray(npts)
#    yy = new_doubleArray(npts)
#    ww = new_doubleArray(npts)
#    for i in range(npts):
#        doubleArray_setitem(xx,i,x[i])
#        doubleArray_setitem(yy,i,y[i])
#        doubleArray_setitem(ww,i,w[i])
#    bbinedgesa = new_doubleArray(nbinsa+1)
#    for i in range(nbinsa+1):
#        doubleArray_setitem(bbinedgesa,i,binedgesa[i])
#    bbincentersb = new_doubleArray(nbinsb)
#    for i in range(nbinsb):
#        doubleArray_setitem(bbincentersb,i,bincentersb[i])
#    bbincentersr = new_doubleArray(nbinsr)
#    for i in range(nbinsr):
#        doubleArray_setitem(bbincentersr,i,bincentersr[i])
#
#    aacc = new_doubleArray(nbinsr*nbinsb*nbinsa)
#
#    houghcircles(aacc,xx,yy,ww,bbinedgesa,bbincentersb,bbincentersr,npts,nbinsa,nbinsb,nbinsr)
#
#    acc = num.zeros(nbinsr*nbinsb*nbinsa)
#    for i in range(nbinsr*nbinsb*nbinsa):
#        acc[i] = doubleArray_getitem(aacc,i)
#    acc = acc.reshape([nbinsr,nbinsb,nbinsa])
#    acc = acc.swapaxes(0,2)
#    return acc

def detectcircles(edgemag,
                  binedgesa=None,bincentersb=None,bincentersr=None,nbinsa=10,
                  nbinsb=10,nbinsr=10,mina=0.,minb=0.,minr=None,
                  maxa=None,maxb=None,maxr=None,
                  peaksnhoodsize=None,peaksthreshold=None,maxncircles=1):

    # set parameters
    (binedgesa,bincentersa,bincentersb,bincentersr,nbinsa,nbinsb,nbinsr,
     peaksnhoodsize,peaksthreshold,maxncircles) = \
     detectcircles_setparameters(edgemag,binedgesa,bincentersb,bincentersr,nbinsa,nbinsb,nbinsr,
                                 mina,minb,minr,maxa,maxb,maxr,peaksnhoodsize,peaksthreshold,maxncircles)

    bw = edgemag>0
    [r,c] = num.where(bw)
    c = c.astype('float')
    r = r.astype('float')
    w = edgemag[bw]
    npts = len(r)
    # find circles using the hough transform
    #acc = houghcircles_wrapper(c,r,w,binedgesa,bincentersb,bincentersr)
    acc = houghcircles(c,r,w,binedgesa,bincentersb,bincentersr)
    
    if peaksthreshold is None:
        peaksthreshold = num.max(acc)/2.

    [idxa,idxb,idxr,score] = houghcirclepeaks(acc,maxncircles,peaksthreshold,peaksnhoodsize)

    #idx = num.argmax(acc)
    #(idxa,idxb,idxr) = ind2sub([nbinsa,nbinsb,nbinsr],idx)

    x = bincentersa[idxa]
    y = bincentersb[idxb]
    r = bincentersr[idxr]

    return (x,y,r)

def ind2sub(sz,ind):

    n = len(sz)
    sub = ()
    for i in range(n-1,0,-1):
        sub = (ind % sz[i],) + sub
        ind = (ind - sub[0])/sz[i]
    sub = (ind,)+sub

    return sub
    
def edge(im,sigma=1.):

    im = im.astype('float')

    m = im.shape[0]
    n = im.shape[1]

    # Magic numbers
    GaussianDieOff = .0001
    PercentOfPixelsNotEdges = .99

    # Design the filters - a Gaussian and its derivative

    # possible widths
    pw = num.array(range(1,31))
    ssq = sigma**2
    width, = num.where(num.exp(-pw**2/(2.*ssq))>GaussianDieOff)
    if len(width) == 0:
        width = 1
    else:
        width = width[-1]

    # gaussian 1D filter
    t = num.array(range(-width,width+1))
    t = t.astype('float')
    gau = num.exp(-(t*t)/(2.*ssq))/(2.*num.pi*ssq)
    
    # Find the directional derivative of 2D Gaussian (along X-axis)
    # Since the result is symmetric along X, we can get the derivative along
    # Y-axis simply by transposing the result for X direction.
    [y,x] = num.mgrid[-width:(width+1),-width:(width+1)]
    dgau2D=-x*num.exp(-(x**2+y**2)/(2.*ssq))/(num.pi*ssq)

    # smooth the image out
    gau = gau.reshape([1,len(t)])
    imSmooth = signal.convolve2d(im,gau,'same','symm')
    imSmooth = signal.convolve2d(imSmooth,gau.T,'same','symm')
    
    # apply directional derivatives
    imx = signal.convolve2d(imSmooth,dgau2D,'same','symm')
    imy = signal.convolve2d(imSmooth,dgau2D.T,'same','symm')

    # compute the squared edge magnitude
    mag = num.sqrt(imx**2 + imy**2)

    # normalize
    magmax = num.max(mag)
    if magmax > 0:
        mag /= magmax

    return mag

def detectcircles_setparameters(im,binedgesa,bincentersb,bincentersr,nbinsa,nbinsb,nbinsr,
                                mina,minb,minr,maxa,maxb,maxr,peaksnhoodsize,peaksthreshold,maxncircles):

    # set parameters
    nr = im.shape[0]
    nc = im.shape[1]
    if maxa is None:
        maxa = float(nc-1)
    if maxb is None:
        maxb = float(nr-1)
    if minr is None:
        minr = min(nr,nc)/4.
    if maxr is None:
        maxr = min(nr,nc)/2.
    if binedgesa is None:
        binedgesa = num.linspace(mina,maxa,nbinsa+1)
    bincentersa = (binedgesa[:-1] + binedgesa[1:])/2.
    if bincentersb is None:
        binedgesb = num.linspace(minb,maxb,nbinsb+1)
        bincentersb = (binedgesb[:-1] + binedgesb[1:])/2.
    if bincentersr is None:
        binedgesr = num.linspace(minr,maxr,nbinsr+1)
        bincentersr = (binedgesr[:-1] + binedgesr[1:])/2.
    nbinsa = len(bincentersa)
    nbinsb = len(bincentersb)
    nbinsr = len(bincentersr)
    
    if peaksnhoodsize is None:
        peakratio = 50.
        peaksnhoodsize = num.array([len(bincentersa)/peakratio,
                                    len(bincentersb)/peakratio,
                                    len(bincentersr)/peakratio])
        peaksnhoodsize = max(2*num.ceil(peaksnhoodsize/2.) + 1, 1)

    return (binedgesa,bincentersa,bincentersb,bincentersr,nbinsa,nbinsb,nbinsr,
            peaksnhoodsize,peaksthreshold,maxncircles)

def draw_circle( img, x, y, r,
                 edgepoint = None,
                 thickness=1,
                 circlecolor=[0,0,0],
                 centercolor=[255,255,255],
                 edgecolor=[0,0,0],
                 windowsize=None, zoomaxes=None ):

    """Draw circle on a color image (MxNx3 numpy array)."""

    if zoomaxes is None:
        zoomaxes = [0,img.shape[1]-1,0,img.shape[0]-1]

    if edgepoint is None:
        edgepoint = [x+r,y]

    pointlists = [[[x,y]],[edgepoint]]
    pointcolors = [centercolor,edgecolor]
    pointsizes = [DCLICK/2,DCLICK/2]
    circlelists = [[[x,y,r]]]
    circlecolors = [circlecolor]
    circlewidths = [thickness]

    bmp = imagesk.draw_annotated_image(img,pointlists=pointlists,
                                       circlelists=circlelists,
                                       windowsize=windowsize,
                                       zoomaxes=zoomaxes,
                                       pointcolors=pointcolors,
                                       circlecolors=circlecolors,
                                       pointsizes=pointsizes,
                                       circlewidths=circlewidths)

    return bmp

