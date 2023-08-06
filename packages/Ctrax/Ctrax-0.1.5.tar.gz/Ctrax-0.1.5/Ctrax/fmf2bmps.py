import os, sys
import FlyMovieFormat
import Image

def main():
    try:
        filename = sys.argv[1]
        args = sys.argv[2:]
        startframe = 0
        endframe = -1
        imgformat = 'bmp'
        outdir = ''
        for i in range(len(args)):
            name,value = args[i].split('=',1)
            name = name.lower()
            if name == '--startframe':
                startframe = int(value)
            elif name == '--endframe':
                endframe = int(value)
            elif name == '--format':
                value = value.lower()
                if not( (value == 'bmp') or (value == 'jpg') or (value == 'png') ):
                    print "Unknown format %s, using default %s"%(value,imgformat)
                else:
                    imgformat = value
            elif name == '--outdir':
                outdir = value

            # end if
        # end for
    except:
        print 'Usage: fmf2bmps fmf_filename'
        print 'Optional arguments:'
        print '--startframe=<startframe> [default = 0]'
        print '--endframe=<endframe> [default = last frame in the fmf]'
        print '--format=<format>, where <format> is an image extension,'
        print '  e.g. bmp, jpg, png [default = bmp]'
        print '--outdir=<output directory> [default = directory containing input fmf'
        print 'Example:'
        print 'fmf2bmps myvideo.fmf --startframe=10 --endframe=100 --format=jpg --outdir=$HOME/tmp'

        sys.exit()
        
    base,ext = os.path.splitext(filename)
    if ext != '.fmf':
        print 'fmf_filename does not end in .fmf'
        sys.exit()
    path,base = os.path.split(base)
    if outdir == '':
        print "saving output %ss to %s"%(imgformat,path)
    else:
        path = outdir

    fly_movie = FlyMovieFormat.FlyMovie(filename)
    n_frames = fly_movie.get_n_frames()
    if endframe < 0 or endframe >= n_frames:
        endframe = n_frames - 1

    for i in xrange(startframe,endframe+1):
        save_frame,timestamp = fly_movie.get_next_frame()
        save_frame = save_frame[::-1,:] # flip for PIL
        h,w=save_frame.shape
        im = Image.fromstring('L',(w,h),save_frame.tostring())
        f='%s_%08d.%s'%(os.path.join(path,base),i,imgformat)
        print 'saving',f
        im.save(f)

if __name__=='__main__':
    main()
    
