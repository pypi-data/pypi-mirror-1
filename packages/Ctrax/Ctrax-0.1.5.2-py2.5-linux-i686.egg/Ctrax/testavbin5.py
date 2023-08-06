import pyglet
import pyglet.media
import numpy as num
import pylab

fn = '/home/kristin/FLIES/data/slawson/slawson_noaudio1.avi'
player = pyglet.media.Player()
source = pyglet.media.load(fn)
player.queue(source)

im = source.get_next_video_frame()
ts1 = source.get_next_video_timestamp()
depth = im.pitch / im.width
imn = num.fromstring(im.data,num.uint8)
imn.resize((im.height,im.width,depth))

pylab.imshow(imn)
pylab.title('timestamp = ' + str(ts1))
pylab.show()

im = source.get_next_video_frame()
ts2 = source.get_next_video_timestamp()
imn = num.fromstring(im.data,num.uint8)
imn.resize((im.height,im.width,depth))

pylab.imshow(imn)
pylab.title('timestamp = ' + str(ts2))
pylab.show()

source._seek(0.0001)

im = source.get_next_video_frame()
ts3 = source.get_next_video_timestamp()
imn = num.fromstring(im.data,num.uint8)
imn.resize((im.height,im.width,depth))

pylab.imshow(imn)
pylab.title('timestamp = ' + str(ts3) + ', should = ' + str(ts1))
pylab.show()

source._seek(0.0001)

im = source.get_next_video_frame()
ts4 = source.get_next_video_timestamp()
imn = num.fromstring(im.data,num.uint8)
imn.resize((im.height,im.width,depth))

pylab.imshow(imn)
pylab.title('timestamp = ' + str(ts4) + ', should = ' + str(ts1))
pylab.show()

source._seek(ts1)

im = source.get_next_video_frame()
ts5 = source.get_next_video_timestamp()
imn = num.fromstring(im.data,num.uint8)
imn.resize((im.height,im.width,depth))

pylab.imshow(imn)
pylab.title('timestamp = ' + str(ts5) + ', should = ' + str(ts2))
pylab.show()
