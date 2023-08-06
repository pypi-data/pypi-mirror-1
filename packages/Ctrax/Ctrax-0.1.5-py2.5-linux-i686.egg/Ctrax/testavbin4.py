import pyglet
import pyglet.media as media
import numpy as num
import pylab as pylab

fn = 'framecount_xvid.avi'
source = media.load(fn)
player = media.Player()
player.queue(source)
player.seek(0)
im = player.get_texture().get_image_data()
imn = num.fromstring(im.data,num.uint8)
depth = len(imn) / im.width / im.height
imn.resize((im.height,im.width,depth))

pylab.imshow(imn)
pylab.title('timestamp = %f'%player.time)
pylab.show()
