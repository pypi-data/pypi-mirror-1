import numpy as num
from movies import CompressedAvi
import pylab

fn = '/home/kristin/FLIES/docs/mtrax_methods_paper/natmethodstext/videos/flybowl_fru1fru1_20090301_204358_xvid_20MB.avi'

movie = CompressedAvi(fn)
print 'start_time = ' + str(movie.start_time)

(frame,ts) = movie.get_next_frame()
pylab.imshow(frame)
pylab.gray()
pylab.title('timestamp = %f'%ts)
pylab.show()


