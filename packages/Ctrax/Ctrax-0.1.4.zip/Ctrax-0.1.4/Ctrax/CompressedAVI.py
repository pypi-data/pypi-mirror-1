import numpy as num
import pyglet.media as media
DEBUG = True

class CompressedAvi:

    """Use pyglet.media to read compressed avi files"""
    def __init__(self,filename):

        self.issbfmf = False
        print 'trying to load ' + filename
        print 'media = ' + str(media)
        self.source = media.load(filename)
        self.ZERO = 0.00001
        self.source._seek(self.ZERO)
        self.start_time = self.source.get_next_video_timestamp()

        # estimate properties of the video that would be nice 
        # to be able to read in -- i have no idea how accurate 
        # these estimates are
        self.duration_seconds = self.source.duration
        self._estimate_fps()
        self.frame_delay_us = 1e6 / self.fps
        self._estimate_keyframe_period()
        self.n_frames = int(num.floor(self.duration_seconds * self.fps))
        print "n_frames estimated to be %d"%self.n_frames
        
        # added to help masquerade as FMF file:
        self.filename = filename

        # read in the width and height of each frame
        self.width = self.source.video_format.width
        self.height = self.source.video_format.height

        self.MAXBUFFERSIZE = num.round(200*1000*1000/self.width/self.height)
        self.buffersize = min(self.MAXBUFFERSIZE,self.keyframe_period)

        # compute the bits per pixel
        self.source._seek(self.ZERO)
        im = self.source.get_next_video_frame()
        im = num.fromstring(im.data,num.uint8)
        self.color_depth = len(im)/self.width/self.height
        if self.color_depth != 1 and self.color_depth != 3:
            raise ValueError( 'color_depth = %d, only know how to deal with color_depth = 1 or colr_depth = 3'%self.color_depth )
        self.bits_per_pixel = self.color_depth * 8

        # allocate the buffer
        self.buffer = num.zeros((self.height,self.width,self.buffersize),dtype=num.uint8)
        self.bufferts = num.zeros(self.buffersize)
        # put the first frame in it
        self.source._seek(self.ZERO)
        self.currframe = 0
        (frame,ts) = self.get_next_frame_and_reset_buffer()

        self._all_timestamps = None

    def get_all_timestamps(self):
        if self._all_timestamps is None:
            self._all_timestamps = []
            for f in range(self.n_frames):
                try:
                    (frame,ts) = self.get_frame(f)
                except:
                    continue
                self._all_timestamps.append(ts)
        return self._all_timestamps            

    def get_frame(self,framenumber):
        """Read frame from file and return as NumPy array."""

        if framenumber < 0: raise IndexError

        # have we already stored this frame?
        if framenumber >= self.bufferframe0 and framenumber < self.bufferframe1:
            off = num.mod(framenumber - self.bufferframe0 + self.bufferoff0,self.buffersize)
            if DEBUG: print "frame %d is in buffer at offset %d"%(framenumber,off)
            return (self.buffer[:,:,off].copy(),self.bufferts[off])

        # is framenumber the next frame to read in?
        if framenumber == self.currframe:
            if DEBUG: print "frame %d is the next frame, just calling get_next_frame"%framenumber
            return self.get_next_frame()

        # otherwise, we need to seek

        # find the last keyframe at or before framenumber
        lastkeyframe = num.floor(framenumber / self.keyframe_period)*self.keyframe_period
        lastkeyframe_s = lastkeyframe / self.fps + self.start_time

        if DEBUG: print "keyframe before frame %d is %d (ts = %f)"%(framenumber,lastkeyframe,lastkeyframe_s)

        didbeginbusy = False
        if params.interactive:
            wx.Yield()
            if not wx.IsBusy():
                didbeginbusy = True
                wx.BeginBusyCursor()

        # is the current frame before the desired frame and at or after the nearest keyframe?
        if framenumber > self.currframe and self.currframe >= lastkeyframe:

            if DEBUG: print "the best thing to do is just to read in frames until we get to desired %d (currframe = %d)"%(framenumber,self.currframe)

            # read into the buffer
            for f in range(self.currframe,framenumber+1):
                try:
                    (frame,ts) = self.get_next_frame()
                except:
                    if didbeginbusy:
                        wx.EndBusyCursor()
                    raise
            
            if didbeginbusy:
                wx.EndBusyCursor()

            return (frame,ts)
            
        # seek around til we find the right window

        if DEBUG: print "we need to seek"

        # make sure we don't move in opposite directions ever
        dirmoved = 0

        # convert from frame to time
        wantts = framenumber / self.fps + self.start_time
        if DEBUG: print "frame %d is equivalent to time stamp %f"%(framenumber,wantts)
        while True:
            # try seeking
            if DEBUG: print "start_time = %f"%self.start_time
            if DEBUG: print "trying to seek to %f (actually %f)"%(lastkeyframe_s,lastkeyframe_s-self.start_time)
            try: 
                self.source._seek(lastkeyframe_s-self.start_time)
            except:
                print 'seeking failed, aborting. tried to seek to %f (actually %f)'%(lastkeyframe_s,lastkeyframe_s-self.start_time)
            tscurr = self.source.get_next_video_timestamp()
            if DEBUG: print "ended up seeking to %f"%tscurr

            # are we in the right ballpark?
            if wantts < tscurr:

                lastkeyframe_s = max(self.ZERO,lastkeyframe_s-self.keyframe_period_s)
                if DEBUG: print "still not back far enough, trying to seek to %f"%lastkeyframe_s
                dirmoved = -1
                continue

            elif wantts >= tscurr + self.keyframe_period_s:
                if dirmoved == -1:
                    # we went back and now we think we need to go forward
                    # so we're screwed up
                    # let's just stay
                    if DEBUG: print "uh oh -- we've already gone backward, and now we think we need to go forward, so we're just going to stay"
                    break
                lastkeyframe_s += self.keyframe_period_s
                dirmoved = 1
                continue
            else:
                # we're in the right ballpark
                if DEBUG: print "we're in the right ballpark"
                break

        # end loop searching for keyframe

        lastkeyframe = (tscurr - self.start_time)*self.fps
        self.currframe = int(lastkeyframe)

        (frame,ts) = self.get_next_frame_and_reset_buffer()

        # go forward until we get the right frame
        for f in range(self.currframe,framenumber+1):
            try:
                (frame,ts) = self.get_next_frame()
            except:
                if didbeginbusy:
                    wx.EndBusyCursor()
                raise

        if didbeginbusy:
            wx.EndBusyCursor()

        # return
        return (frame,ts)

    def get_next_frame_and_reset_buffer(self):
        
        self.bufferframe0 = self.currframe
        self.bufferframe1 = self.currframe + 1
        self.bufferoff0 = 0
        self.bufferoff = 1
        (frame,ts) = self._get_next_frame_helper()
        self.buffer[:,:,0] = frame.copy()
        self.bufferts[0] = ts

        # set the current frame
        self.currframe += 1
        self.prevts = ts

        return (frame,ts)

    def _get_next_frame_helper(self):
        ts = self.source.get_next_video_timestamp()
        if ts is None:
            if self.currframe - 1 < self.n_frames:
                self.n_frames = self.currframe - 1
            raise NoMoreFramesException
        im = self.source.get_next_video_frame()
        frame = num.fromstring(im.data,num.uint8)

        if self.color_depth == 1:
            frame.resize((im.height,im.width))
        else: # color_depth == 3
            frame.resize( (self.height, self.width*3) )
            tmp = frame.astype(float)
            tmp = tmp[:,2:self.width*3:3]*.3 + \
                tmp[:,1:self.width*3:3]*.59 + \
                tmp[:,0:self.width*3:3]*.11
            frame = tmp.astype(num.uint8)

        frame = num.flipud(frame)

        return (frame,ts)

    def get_next_frame(self):

        (frame,ts) = self._get_next_frame_helper()

        # store 

        # last frame stored will be 1 more
        self.bufferframe1 += 1

        # are we erasing the first frame?
        if self.bufferoff0 == self.bufferoff:
            self.bufferframe0 += 1
            self.bufferoff0 += 1
            if DEBUG: print "erasing first frame, bufferframe0 is now %d, bufferoff0 is now %d"%(self.bufferframe0,self.bufferoff0)

        if DEBUG: print "buffer frames: [%d,%d), bufferoffset0 = %d"%(self.bufferframe0,self.bufferframe1,self.bufferoff0)
            
        self.buffer[:,:,self.bufferoff] = frame.copy()
        self.bufferts[self.bufferoff] = ts

        if DEBUG: print "read into buffer[%d], ts = %f"%(self.bufferoff,ts)

        self.bufferoff += 1

        # wrap around
        if self.bufferoff == self.buffersize:
            self.bufferoff = 0

        if DEBUG: print "incremented bufferoff to %d"%self.bufferoff

        # remember current location in the movie
        self.currframe += 1
        self.prevts = ts

        if DEBUG: print "updated currframe to %d, prevts to %f"%(self.currframe,self.prevts)

        return (frame,ts)

    def _estimate_fps(self):

        # seek to the start of the stream
        self.source._seek(self.ZERO)

        # initial time stamp
        ts0 = self.source.get_next_video_timestamp()
        ts1 = ts0

        # get the next frame and time stamp a bunch of times
        nsamples = 200
        i = 0 # i is the number of frames we have successfully grabbed
        while True:
            im = self.source.get_next_video_frame()
            ts = self.source.get_next_video_timestamp()
            if num.isnan(ts) or (ts <= ts0):
                break
            i = i + 1
            ts1 = ts
            if i >= nsamples:
                break
        
        if ts1 <= ts0:
            raise ValueError( "Could not compute the fps in the compressed movie" )

        self.fps = float(i) / (ts1-ts0)
        print 'Estimated frames-per-second = %f'%self.fps
        
    def _estimate_keyframe_period(self):

        self.source._seek(self.start_time)
        ts0 = self.source.get_next_video_timestamp()
        i = 1 # i is the number of successful seeks
        foundfirst = False
        while True:

            # seek to the next frame
            self.source._seek(float(i)/self.fps)

            # get the current time stamp
            ts = self.source.get_next_video_timestamp()

            # did we seek past the end of the movie?
            if num.isnan(ts):
                raise ValueError( "Could not compute keyframe period in compressed video" )    
                break

            if ts > ts0:
                if foundfirst:
                    break
                else:
                    foundfirst = True
                    i0 = i
                    ts0 = ts

            i = i + 1

        if DEBUG: print "i = %d, i0 = %d"%(i,i0)
        self.keyframe_period = i - i0
        self.keyframe_period_s = self.keyframe_period / self.fps
        print "Estimated keyframe period = " + str(self.keyframe_period)

    def get_n_frames( self ):
        return self.n_frames

    def get_width( self ):
        return self.width

    def get_height( self ):
        return self.height

    def seek(self,framenumber):

        ts = float(framenumber) / self.fps + self.start_time
        self.source._seek(ts)
        ts = self.source.get_next_video_timestamp()
        self.prevts = ts - 1. / self.fps
        self.currframe = (ts - self.start_time)*self.fps

        return self.currframe

