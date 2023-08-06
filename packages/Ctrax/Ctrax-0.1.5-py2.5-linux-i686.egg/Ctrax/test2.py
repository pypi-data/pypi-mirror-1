import sys
import time

test = 1

try:
    if test == 1:
        for i in range(1000000):
            try:
                print str(i)
                time.sleep(1)
            except IOError:
                print "Exception!"
                break
    elif test == 2:
        f = open("tmp.txt","r")
        f.seek(1000000000000000)
        print "tell = " + str(f.tell())
        f.close()
except KeyboardInterrupt:
    print "User interrupt!"
    raise
print "out of loop"
