class el:
    def __init__(self,x=0,y=0):
        self.x = x
        self.y = y
    def __str__(self):
        return '[x: ' + str(self.x) + ', y: ' + str(self.y) + ']'

class ar:
    def __init__(self):
        self.buffer = dict()
    def __getitem__(self,i):
        return self.buffer[i]
    def __setitem__(self,i,val):
        self.buffer[i] = val

el1 = el(1,2)
ar1 = ar()
ar2 = ar()
ar1[10] = el1
ar2[20] = ar1
ar2[20][10].x = 10

print 'ar2[20][10] = ' + str(ar2[20][10])
