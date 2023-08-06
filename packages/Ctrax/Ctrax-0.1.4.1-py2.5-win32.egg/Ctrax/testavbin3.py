import numpy as num
from CompressedAVI import CompressedAvi
import pylab

fn = 'framecount_xvid.avi'

movie = CompressedAvi(fn)
print 'start_time = ' + str(movie.start_time)

(frame,ts) = movie.get_next_frame()
pylab.imshow(frame)
pylab.gray()
pylab.title('timestamp = %f'%ts)
pylab.show()


