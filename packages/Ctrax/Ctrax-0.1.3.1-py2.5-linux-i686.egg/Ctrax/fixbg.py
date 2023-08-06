import wx
from params import params
from wx import xrc
import motmot.wxvideo.wxvideo as wxvideo
#import motmot.wxglvideo.simple_overlay as wxvideo
import imagesk
import numpy as num
import pkg_resources # part of setuptools
import colormapk

RSRC_FILE = pkg_resources.resource_filename( __name__, "fixbg.xrc" )

USEGL = False

class FixBG:

    def __init__(self,parent,bgmean,bgstd):
        self.parent = parent
        self.im = bgmean.copy()
        self.bgmean = bgmean
        self.bgstd = bgstd
        rsrc = xrc.XmlResource(RSRC_FILE)
        self.frame = rsrc.LoadFrame(parent,"fixbg_frame")

        self.InitControlHandles()
        self.InitializeValues()
        self.BindCallbacks()
        self.OnResize()
        self.ShowImage()

    def control(self,ctrlname):
        return xrc.XRCCTRL(self.frame,ctrlname)

    def InitControlHandles(self):

        self.done_button = self.control('done_button')
        self.cancel_button = self.control('cancel_button')
        self.undo_button = self.control('undo_button')
        self.closewithoutsaving_button = self.control('closewithoutsaving_button')
        self.saveandclose_button = self.control('saveandclose_button')
        self.img_panel = self.control('img_panel')
        box = wx.BoxSizer( wx.VERTICAL )
        self.img_panel.SetSizer( box )
        self.img_wind = wxvideo.DynamicImageCanvas( self.img_panel, -1 )
        self.img_wind.set_resize(True)
        box.Add( self.img_wind, 1, wx.EXPAND )
        self.img_panel.SetAutoLayout( True )
        self.img_panel.Layout()

    def InitializeValues(self):

        wx.BeginBusyCursor()
        wx.Yield()

        imblank = num.zeros(self.im.shape+(3,),dtype=num.uint8)
        self.img_wind.update_image_and_drawings('fixbg',imblank,
                                                format='RGB8')
        self.img_wind_child = self.img_wind.get_child_canvas('fixbg')
        self.polygons = []
        (nc,nr) = self.im.shape
        [self.X,self.Y] = mgrid[0:nc,0:nr]
        self.CreateFixedMean()

        # set click mode
        self.selected_point = 'none'
        
        wx.EndBusyCursor()

    def BindCallbacks(self):

        # buttons: to do

        # mouse click
        self.img_wind_child.Bind(wx.EVT_LEFT_DOWN,self.MouseDown)
        self.img_wind_child.Bind(wx.EVT_LEFT_UP,self.MouseUp)

    def CreateFixedMean(self,fixstd=False):

        wx.BeginBusyCursor()
        wx.Yield()
        self.bgmean_fixed = fix_holes(self.bgmean,self.polygons)
        if fixstd:
            self.bgstd_fixed = fix_holes(self.bgstd,self.polygons)
        self.img_shown = imagesk.double2mono8(self.bgmean_fixed,donormalize=False)
        wx.EndBusyCursor()

    def fix_holes(self,im,polygons):

        s = num.ones((2,2),bool)        
        for i in range(len(polygons)):

            # get points on the inside of the polygon
            isin = point_inside_polygon(X,Y,polygons[i])
            (y_isin,x_isin) = nonzero(isin)
            
            # get points on the outside boundary of the polygon
            isboundary = logical_and(morph.binary_dilation(isin,s),
                                     ~isin)
            (y_isboundary,x_isboundary) = nonzero(isboundary)

            for j in range(len(r)):
                x = x_isin[j]
                y = y_isin[j]
                d = num.sqrt((y_isboundary-y)**2+(x_isbounary-x)**2)
                w = num.exp(-d)
                z = im[isboundary] * w
                                               
        
    def point_inside_polygon(x,y,poly):
        # from http://www.ariel.com.au/a/python-point-int-poly.html
        # by Patrick Jordan

        n = len(poly)
        inside = False

        p1x,p1y = poly[0]
        for i in range(n+1):
            p2x,p2y = poly[i % n]
            if y > min(p1y,p2y):
                if y <= max(p1y,p2y):
                    if x <= max(p1x,p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x,p1y = p2x,p2y

        return inside


