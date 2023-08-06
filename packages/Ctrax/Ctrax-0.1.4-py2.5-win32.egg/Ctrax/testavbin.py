import pyglet
import pyglet.media as media
import numpy as num
import pylab

fn = 'framecount_xvid.avi'
fps = 15.
source = media.load(fn)
ts = source.get_next_video_timestamp()
im = source.get_next_video_frame()
depth = im.pitch / im.width
imn = num.fromstring(im.data,num.uint8)
imn.resize((im.height,im.width,depth))
pylab.imshow(imn)
pylab.title('timestamp = %f'%ts)
pylab.show()
