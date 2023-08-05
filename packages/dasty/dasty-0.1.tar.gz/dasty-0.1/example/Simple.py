"""A simple test.

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.
"""

import dasty
import numpy
import OpenGLContext.testingcontext
import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT
import sys

BaseContext,MainFunction = OpenGLContext.testingcontext.getInteractive(['glut'])
scene = dasty.core.Scene()

RAD_TO_DEG = 57.295779513082323

class DrawVisitor:
    def draw_mmm(self, mmm):
        if not mmm.primitive is mmm.EMPTY_PRIMITIVE:
            # Project primitive on screen
            pass

class TestContext(BaseContext):

    def OnInit(self):
        #GLUT.glutInit(sys.argv)
        self.first_render = True

    def Render(self, mode=None): 
        scene.primitive.gl_draw(None, None) # XXX

        if self.first_render:
            # test projection, TODO test view.. mettre dans test
            x=1.0
            y=1.0
            z=1.0
            w=10.0

            GL.glMatrixMode(GL.GL_PROJECTION)
            GL.glLoadIdentity()
            GLU.gluPerspective(RAD_TO_DEG * x, y, z, w)
            matrix1 = GL.glGetDoublev(GL.GL_PROJECTION_MATRIX)

            vp = dasty.core.ViewPlatform()
            vp.set_frustum(x,y,z,w)
            matrix2 = vp.gl_projection

            m = (matrix1 - matrix2)
            dif = numpy.sum(m*m)
            print dif
            if dif < 0.001:
                print "Test Projection Matrix OK"
            else:
                print "Test Projection Matrix NOT OK"

            self.first_render = False
            GLUT.glutLeaveMainLoop()

class Cube(dasty.core.Primitive):
    def __init__(self, size):
        dasty.core.Primitive.__init__(self)
        self.size = size
    def gl_draw(self, viewplatform, wsize):
        GLUT.glutSolidCube(1.0)

def main():
    cube1 = Cube(1.0)
    scene.primitive = cube1
    MainFunction(TestContext)

if __name__ == "__main__":
    main()
