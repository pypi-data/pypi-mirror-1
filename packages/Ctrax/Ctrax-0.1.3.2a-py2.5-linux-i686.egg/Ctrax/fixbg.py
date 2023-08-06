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

        self.undo_button = self.control('undo_button')
        self.close_button = self.control('close_button')
        self.done_button = self.control('done_button')
        self.cancel_button = self.control('cancel_button')

        self.undo_button.Enable(False)
        self.close_button.Enable(False)

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

        # all pixel locations in the image,
        # for checking which pixels are in the polygon
        (self.X,self.Y) = mgrid[0:nc,0:nr]

        # initialize fixed bgmean to just the bgmean
        self.bgmean_fixed = self.bgmean.copy()
        # same for std
        self.bgstd_fixed = self.bgstd.copy()

        # initialize to show mean
        self.showmean = True

        # set click mode
        self.selected_point = 'none'
        
        wx.EndBusyCursor()

    def BindCallbacks(self):

        # buttons: to do

        # mouse click
        self.img_wind_child.Bind(wx.EVT_LEFT_DOWN,self.MouseDown)
        self.img_wind_child.Bind(wx.EVT_LEFT_UP,self.MouseUp)

    def AddPolygon(self):

        wx.BeginBusyCursor()
        wx.Yield()
        self.fix_hole(self.bgmean,self.bgmean_fixed,self.polygons[-1])
        self.fix_hole(self.bgstd,self.bgstd_fixed,self.polygons[-1])
        self.undo_button.Enable(True)
        self.close_button.Enable(False)
        self.UpdateImageShown()
        self.Redraw()
        wx.EndBusyCursor()

    def ShowImage(self):

        polygoncolor = (255,0,0)
        lines = []
        for i in range(len(self.polygons)-1):
            for j in range(self.polygons[i].shape[0]):
                lines.append(imagesk.draw_line(self.polygons[i][j,0],
                                               self.polygons[i][j,1],
                                               self.polygons[i][j+1,0],
                                               self.polygons[i][j+1,1],
                                               polygoncolor))
        (lines,linecolors) = imagesk.separate_linesegs_colors(lines)
        if self.showmean:
            self.img_shown = imagesk.double2mono8(self.bgmean_fixed,donormalize=False)
        else:
            self.img_shown = imagesk.double2mono8(self.bgstd_fixed,donormalize=False)
        self.img_wind.update_image_and_drawings('fixbg',self.image_shown,
                                                format="RGB8",
                                                linesegs = lines,
                                                lineseg_colors=linecolors)
        self.img_wind.Refresh(eraseBackground=False)
        
    def MouseUp(self,evt):
        pass

    def MouseDown(self,evt):
        pass

    def RemovePolygon(self):
        wx.BeginBusyCursor()
        wx.Yield()
        self.undo_fix_hole(self.bgmean,self.bgmean_fixed,self.polygons[-1])
        self.undo_fix_hole(self.bgstd,self.bgstd_fixed,self.polygons[-1])
        self.polygons[-1] = []
        self.UpdateImageShown()
        wx.EndBusyCursor()

    def fix_hole(im,out,polygon):

        s = num.ones((3,3),bool)        

        # get points on the inside of the polygon
        isin = point_inside_polygon(self.X,self.Y,polygon)
        (y_isin,x_isin) = num.nonzero(isin)

        # get points on the outside boundary of the polygon
        isboundary = num.logical_and(morph.binary_dilation(isin,s),
                                     ~isin)

        (y_isboundary,x_isboundary) = num.nonzero(isboundary)

        # for each point inside the polygon, get an average from
        # all the boundary points
        for i in range(len(y_isin)):
            x = x_isin[i]
            y = y_isin[i]
            d = num.sqrt((y_isboundary-y)**2+(x_isboundary-x)**2)
            w = num.exp(-d)
            out[y,x] = num.sum(im[isboundary] * w) / num.sum(w)

    def undo_fix_hole(im0,im,polygon):
        isin = point_inside_polygon(self.X,self.Y,polygon)
        im[isin] = im0[isin]    

def point_inside_polygon(x,y,poly):
    # adapted from http://www.ariel.com.au/a/python-point-int-poly.html
    # by Patrick Jordan

    n = len(poly)
    inside = num.zeros(x.shape,dtype=bool)
    xinters = num.zeros(x.shape)

    p1x,p1y = poly[0]
    idx2 = num.zeros(x.shape,dtype=bool)
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        idx = num.logical_and(y > min(p1y,p2y),
                              num.logical_and(y <= max(p1y,p2y),
                                              x <= max(p1x,p2x)))
        if p1y != p2y:
            xinters[idx] = (y[idx]-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
        if p1x == p2x:
            inside[idx] = ~inside[idx]
        else:
            idx2[:] = False
            idx2[idx] = x[idx] <= xinters[idx]
            inside[idx2] = ~inside[idx2]
        p1x,p1y = p2x,p2y

    return inside
