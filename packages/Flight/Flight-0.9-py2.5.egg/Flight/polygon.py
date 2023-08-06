import OpenGL.GL
class poly:
    def __init__(self,verticies,normal,color):
        self.color=color
        self.verticies=verticies
        self.normal=normal
        self.d=0.5
    def draw(self):
        OpenGL.GL.glBegin(GL_POLYGON)
        OpenGL.GL.glNormal(self.normal[0],self.normal[1],self.normal[2])
        OpenGL.GL.glColor3f(self.color[0], self.color[1], self.color[2])
        for i in self.verticies:
            #print self.verticies[i][0],self.verticies[i][1],self.verticies[i][2]
            OpenGL.GL.glVertex3f(self.verticies[i][0]/self.d,self.verticies[i][1]/self.d,self.verticies[i][2])
        OpenGL.GL.glEnd()
