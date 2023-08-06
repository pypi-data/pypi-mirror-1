from slut import *
class FlightWorld(World):
    def onJoyAxisMotion(self, event):
        if event.axis==5:
            self.hatx=event.value
            self.hatMoved()
        elif event.axis==4:
            self.haty=event.value
            self.hatMoved()
        elif event.axis==0:
            self.xaxis=event.value
            self.xyMoved()
        elif event.axis==1:
            self.yaxis=event.value
            self.xyMoved()
        else:
            print event.axis
            print event.value
    def xyMoved(self):
        if self.xaxis==0 and self.yaxis==0:
            self.camera.cancelThrustRot()
        self.camera.rotBy(Thrust(0,0,self.yaxis))        
        #self.camera.rotBy(Thrust(self.xaxis,self.yaxis,0))
        print self.xaxis,self.yaxis
    def hatMoved(self):
        if not (self.hatx==0 and self.haty==0): 
            self.camera.rotTo(0,self.haty*90,(self.hatx-1)*90)
    def onJoyButtonDown(self,event):
        if event.button==1:
            self.camera.rotTo(0,0,0)
        elif event.button==2:
            self.speed+=1
            self.speed=min(self.speed,20)
            self.speedChanged()
        elif event.button==3:
            self.speed-=1
            self.speed=max(self.speed,-1)
            self.speedChanged()
        print event.button
    def speedChanged(self):
        self.camera.moveBy(Thrust(0,0,self.speed))
    def onJoyHatMotion(self, event):
        print "current hat position", event.hat
    def onSetup(self):
        self.width=400
        self.height=300
        self.name="Flight"
        self.hatx=0
        self.haty=0
        self.xaxis=0
        self.yaxis=0
        self.speed=-1
        self.camera.moveBy(Thrust(0,0,1))
    def onDraw(self):
        glBegin(GL_LINE_STRIP)
        glVertex(0.0,0.0,0.0)
        glVertex(1.0,0.0,0.0)
        glVertex(1.0,1.0,0.0)
        glVertex(-0.5,1.5,0.0)
        glVertex(0.0,0.0,0.0)
        glEnd()
myworld=FlightWorld()
myworld.run()
import sys
sys.exit(0)
