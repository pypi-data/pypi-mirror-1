from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
import polygon
v={}
v['0']=[0,0,0]
v['1']=[0,1,0]
v['2']=[1,0,0]
v1={}
v1['0']=[0,0,0]
v1['1']=[0,-1,0]
v1['2']=[-1,0,0]
v2={}
v2['0']=[0.5,0.5,0]
v2['1']=[-0.5,0.5,0]
v2['2']=[-0.5,-0.5,0]
v2['3']=[0.5,-0.5,0]


mypoly=polygon.poly(v,[1.0, 0.0, 0.0])
mypoly2=polygon.poly(v1,[0.0,1.0,0.0])
laserset={}
lasercount=0
polyset={}
polyset['0']=mypoly
polyset['1']=mypoly2
def movelaser():
    for i in laserset:
        laserset[i].d+=0.1
        if laserset[i].d==1000:
            del laserset[i]
def DrawGLScene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    for i in polyset:
        polyset[i].draw()
    for i in laserset:
        laserset[i].draw()
    movelaser()
    glutSwapBuffers()
def Joystick(buttonMask,x,y,z):
    print buttonMask
def specialKey(k,x,y):
    print k
def KeyPressed(*args):
    global mypoly,mypoly2,mypoly3,lasercount,laserset
    if args[0]=='q':
        sys.exit(0)
    if args[0]=='a':
        mypoly.d+=1
    if args[0]=='z':
        mypoly.d-=1
    if args[0]=='w':
        mypoly2.d+=1
    if args[0]=='s':
        mypoly2.d-=1
    if args[0]==' ':
        lasercount+=1
        mylaser=polygon.poly(v2,[1.0,1.0,1.0])
        laserset[lasercount]=mylaser
        print 'fire'
    #print args
    
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    window = glutCreateWindow("Williams Flight simulation pre-alpha")
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glutDisplayFunc(DrawGLScene)
    glutIdleFunc(DrawGLScene)
    glutJoystickFunc(Joystick)
    glLoadIdentity()
    glutFullScreen()
    glutKeyboardFunc(KeyPressed)
    glutSpecialFunc(specialKey)
    glutMainLoop()
    
main()