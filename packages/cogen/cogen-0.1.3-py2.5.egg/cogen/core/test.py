
#~ import sys
#~ import traceback
#~ import inspect
#~ def a():
    #~ yield 1
    #~ yield 2
    #~ yield 3
    
#~ def b():
    #~ c()
    
#~ def c():
    #~ x = a()
    #~ x.next()
    #~ x.throw(Exception, Exception('bla'))
#~ b()

class a(object):
    def __init__(t, a=1):
        print 'a',a
class b(a):
    pass
class c(b):
    def __init__(t, x=1, **kws):
        super(t.__class__, t).__init__(**kws)
        print x, kws
        
x = c()
