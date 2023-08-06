import OpenGL.GL
from Flight.polygon import poly
class dustParticle:
    def __init__(self,x,y,z):
        self.color=[1.0,1.0,1.0]
        self.location=[x,y,z]
        self.polylist={}
        for i in __builtins__.range(6):
            normal={}
            normal=[0.0,0.0,0.0]
            if i%2==1:
                ndir=1
            else:
                ndir=-1
            normal[i/2]=ndir
            v={}
            n=0
            for px in [1,-1]:
                for py in [1,-1]:
                    v[__builtins__.str(n)]=[0.0,0.0,0.0]
                    if i>1:
                        v[__builtins__.str(n)][0]=px
                    else:
                        v[__builtins__.str(n)][1]=px
                    if i<4:
                        v[__builtins__.str(n)][2]=py
                    else:
                        v[__builtins__.str(n)][1]=py
                    n+=1           
            print v
            self.polylist[i]=poly(v,normal,[0.0,0.0,0.0])

a=dustParticle(0.0,0.0,0.0)
