import pyglet
import pyglet.media as media
import numpy as num
import pylab as pylab

fn = '/home/kristin/FLIES/data/jwaters/Pogo_FCP2.avi'
#fn = '/home/kristin/FLIES/data/test/framecount.avi'
fps = 20.
source = media.load(fn)
im = source.get_next_video_frame()
ts1 = source.get_next_video_timestamp()
print 'ts1 = ' + str(ts1)
im = source.get_next_video_frame()
ts2 = source.get_next_video_timestamp()
print 'ts2 = ' + str(ts2)
ZERO = 0.00001
#ZERO = 2*ts1-ts2
print 'ZERO = ' + str(ZERO)
#source._seek(ZERO)
im = source.get_next_video_frame()
ts = source.get_next_video_timestamp()
print 'ts = ' + str(ts)
print 'im = ' + str(im)
depth = im.pitch / im.width
imn = num.fromstring(im.data,num.uint8)
imn.resize((im.height,im.width,depth))
pylab.imshow(imn)
pylab.title('timestamp = ' + str(ts))
pylab.show()
