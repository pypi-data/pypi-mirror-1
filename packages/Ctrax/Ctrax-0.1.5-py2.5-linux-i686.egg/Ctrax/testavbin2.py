import pyglet
import pyglet.media as media
import numpy as num
import pylab as pylab
import numpy.random as rand

#fn = '/home/kristin/FLIES/docs/mtrax_methods_paper/movies/encounter_1_16_510.avi'
fn = '/home/kristin/FLIES/docs/mtrax_methods_paper/natmethodstext/videos/flybowl_fru1fru1_20090301_204358_xvid_20MB.avi'
#fps = 20.
depth = 3
source = media.load(fn)
duration = source.duration
print 'duration = ' + str(duration)
print 'width = ' + str(source.video_format.width)
player = media.Player()
player.queue(source)

def estimate_fps():

    # seek to the start of the stream
    player.seek(0)

    # initial time stamp
    ts0 = source.get_next_video_timestamp()
    ts1 = ts0

    # get the next frame and time stamp a bunch of times
    nsamples = 200
    i = 0 # i is the number of frames we have successfully grabbed
    while True:
        im = source.get_next_video_frame()
        ts = source.get_next_video_timestamp()
        if num.isnan(ts) or (ts <= ts0):
            break
        i = i + 1
        ts1 = ts
        if i >= nsamples:
            break

    if ts1 <= ts0:
        raise ValueError( "Could not compute the fps in the compressed movie" )

    fps = num.double(i) / (ts1-ts0)
    print 'Estimated frames-per-second = %f'%fps
    return fps

fps = estimate_fps()

def estimate_keyframe_period():

    player.seek(0)
    ts0 = source.get_next_video_timestamp()
    i = 1 # i is the number of successful seeks
    foundfirst = False
    while True:

        # seek to the next frame
        print "seeking to " + str(float(i)/fps)
        player.seek(float(i)/fps)

        # get the current time stamp
        ts = source.get_next_video_timestamp()

        # did we seek past the end of the movie?
        if num.isnan(ts):
            raise ValueError( "Could not compute keyframe period in compressed video" )    
            break

        if ts > ts0:
            if foundfirst:
                print "found second difference at i = %d"%i
                break
            else:
                print "found first difference at i = %d"%i
                foundfirst = True
                i0 = i
                ts0 = ts

        i = i + 1
    
    keyframe_period = i - i0
    print "Estimated keyframe period = " + str(keyframe_period)
    return keyframe_period

keyframe_period = estimate_keyframe_period()

# Debug script 1: plots result of seeking around
if True:

    x = num.arange(0.,200,.2)
    idx = rand.permutation(len(x))
    rand.shuffle(x)
    y = num.zeros(x.shape)
    for j in range(len(x)):
        i = idx[j]
        player.seek(x[i])
        y[i] = source.get_next_video_timestamp()
        #im = source.get_next_video_frame()
        #imn = num.fromstring(im.data,num.uint8)
        #imn.resize((im.height,im.width,depth))
        #pylab.imshow(imn)
        #pylab.title('i = %d, timestamp = %f'%(i,y[i]))
        #pylab.show()

        print 'x[%d] = %f, y[%d] = %f'%(i,x[i],i,y[i])

    print '\n\n***Now in order:***'

    for i in range(len(x)):
        print 'x[%d] = %f, y[%d] = %f'%(i,x[i],i,y[i])

    pylab.plot(x,y,'.')
    pylab.show()

else:

    # Debug script 2: seeks once, then reads in frames in order

    player.seek(600./fps)
    for i in range(100):
        ts = source.get_next_video_timestamp()
        im = source.get_next_video_frame()
        imn = num.fromstring(im.data,num.uint8)
        imn.resize((im.height,im.width,depth))
        pylab.imshow(imn)
        pylab.title('i = %d, timestamp = %f'%(i,ts))
        pylab.show()

