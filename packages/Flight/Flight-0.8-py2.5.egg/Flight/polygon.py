from OpenGL.GL import *
class poly:
    def __init__(self,verticies,color):
        self.color=color
        self.verticies=verticies
        self.d=0.5
    def draw(self):
        glBegin(GL_POLYGON)
        glColor3f(self.color[0], self.color[1], self.color[2])
        for i in self.verticies:
            #print self.verticies[i][0],self.verticies[i][1],self.verticies[i][2]
            glVertex3f(self.verticies[i][0]/self.d,self.verticies[i][1]/self.d,self.verticies[i][2])
        glEnd()
