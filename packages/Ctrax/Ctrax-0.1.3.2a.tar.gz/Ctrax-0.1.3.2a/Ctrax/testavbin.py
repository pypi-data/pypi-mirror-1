import pyglet
import pyglet.media as media
import numpy as num
import pylab as pylab

fn = '/home/kristin/FLIES/docs/mtrax_methods_paper/flybowl_fru1fru1_20090301_204358_xvid_30MB.avi';
fps = 20.
source = media.load(fn)
ts = source.get_next_video_timestamp()
im = source.get_next_video_frame()
depth = im.pitch / im.width
imn = num.fromstring(im.data,num.uint8)
imn.resize((im.height,im.width,depth))
pylab.imshow(imn)
pylab.title('timestamp = %f'%ts)
pylab.show()
