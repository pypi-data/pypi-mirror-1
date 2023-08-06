from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys
class poly:
    def __init__(self,verticies,color):
        self.color=color
        self.verticies=verticies
    def draw(self):
        glBegin(GL_POLYGON)
        glColor3f(self.color[0], self.color[1], self.color[2])
        for i in self.verticies:
            #print self.verticies[i][0],self.verticies[i][1],self.verticies[i][2]
            glVertex3f(self.verticies[i][0],self.verticies[i][1],self.verticies[i][2])
        glEnd()
v={}
v['0']=[0,0,0]
v['1']=[0,1,0]
v['2']=[1,0,0]
v1={}
v1['0']=[0,0,0]
v1['1']=[0,-1,0]
v1['2']=[-1,0,0]

mypoly=poly(v,[1.0, 0.0, 0.0])
mypoly2=poly(v1,[0.0,1.0,0.0])
def DrawGLScene():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    mypoly.draw()
    mypoly2.draw()
    glutSwapBuffers()
def KeyPressed(*args):
    print args
    
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(640, 480)
    window = glutCreateWindow("Jeff Molofee's GL Code Tutorial ... NeHe '99")
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glutDisplayFunc(DrawGLScene)
    glutIdleFunc(DrawGLScene)
    glLoadIdentity()
    glutKeyboardFunc(KeyPressed)
    glutMainLoop()
    
main()