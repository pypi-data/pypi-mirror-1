import pyglet
import pyglet.media as media
import numpy as num
import pylab as pylab

fn = '/home/kristin/FLIES/docs/mtrax_methods_paper/movies/encounter_1_16_510.avi'
fps = 20.
source = media.load(fn)
player = media.Player()
player.queue(source)

# Debug script 1: plots result of seeking around
if True:

    x = num.arange(0.,44,.05)
    y = num.zeros(x.shape)
    for i in range(len(x)):
       player.seek(x[i])
       y[i] = source.get_next_video_timestamp()

    pylab.plot(x,y,'.-')
    pylab.show()

else:

    # Debug script 2: seeks once, then reads in frames in order

    player.seek(5./fps)
    depth = 3
    for i in range(10):
        ts = source.get_next_video_timestamp()
        im = source.get_next_video_frame()
        imn = num.fromstring(im.data,num.uint8)
        imn.resize((im.height,im.width,depth))
        pylab.imshow(imn)
        pylab.title('i = %d, timestamp = %f'%(i,ts))
        pylab.show()
