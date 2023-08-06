import numpy as num
import scipy.ndimage.morphology as morph
import matplotlib.pyplot as plt

def fix_hole(im,out,polygon):

    s = num.ones((3,3),bool)        

    # get points on the inside of the polygon
    isin = point_inside_polygon(X,Y,polygon)
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
    isin = point_inside_polygon(X,Y,polygon)
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

# test stuff
im0 = num.random.ranf((100,200))
theta = num.linspace(0,2*num.pi,21)
theta = theta[:-1]
r = 30
mux = 50
muy = 100
poly = num.zeros((len(theta),2))
poly[:,0] = r*num.cos(theta) + mux
poly[:,1] = r*num.sin(theta) + muy

(nc,nr) = im0.shape
(X,Y) = num.mgrid[0:nc,0:nr]

im1 = im0.copy()
fix_hole(im0,im1,poly)

plt.imshow(im1.T)
plt.hold(True)
plt.plot(poly[:,0],poly[:,1],'k.-')
plt.axis('image')
plt.title('interpolated hole')
plt.show()

undo_fix_hole(im0,im1,poly)
plt.imshow(im1.T)
plt.hold(True)
plt.plot(poly[:,0],poly[:,1],'k.-')
plt.axis('image')
plt.title('undid interpolate hole')
plt.show()
