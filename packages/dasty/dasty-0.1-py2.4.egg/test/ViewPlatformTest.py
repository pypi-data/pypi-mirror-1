"""A simple test.

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.
"""

import dasty
import numpy
import OpenGLContext.glutinteractivecontext
import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT
import sys
import unittest

RAD_TO_DEG = 57.295779513082323

def print_format(name, matrix, format):
    m = matrix
    l = len(name)
    f = format
    line_format = f + " " + f + " " + f + " " + f

    print 
    print name, ("= / " + line_format + " \\") % tuple(m[0].tolist())
    print " " * l, (" |  " + line_format + "  |") % tuple(m[1].tolist())
    print " " * l, (" |  " + line_format + "  |") % tuple(m[2].tolist())
    print " " * l, ("  \\ " + line_format + " /") % tuple(m[3].tolist())

class ViewPlatformTest(unittest.TestCase):

    def runTest(self):

        class TestContext(OpenGLContext.glutinteractivecontext.GLUTInteractiveContext):

            test_results = []

            def Render(self, mode=None):
                tests = []

                tproj1 = self.test_projection(fovy=1.0, aspect=1.0, zNear=1.0, zFar=10.0)
                tproj2 = self.test_projection(fovy=2.0, aspect=1.5, zNear=1.0, zFar=2.0)
                tproj3 = self.test_projection(fovy=0.2, aspect=0.4, zNear=0.1, zFar=1000.0)

                tests.append((tproj1, "Test ViewPlatform.gl_projection 1"))
                tests.append((tproj2, "Test ViewPlatform.gl_projection 2"))
                tests.append((tproj3, "Test ViewPlatform.gl_projection 3"))

                tview1 = self.test_view((0.0, 0.0, 0.0), (1.0,-3.0,1.0,6.0))
                tview2 = self.test_view((1.0, 2.0, 3.0), (1.0,0.0,0.0,0.0))
                tview3 = self.test_view((1.0, -2.0, -3.0), (0.0,1.0,0.0,numpy.pi))
                tview4 = self.test_view((1.0, -2.0, -3.0), (0.0,1.0,0.0,numpy.pi/2.0))
                tview5 = self.test_view((1.1, -2.1, -3.2), (1.23,-2.43,0.1,12.55))

                tests.append((tview1, "Test ViewPlatform.gl_view 1"))
                tests.append((tview2, "Test ViewPlatform.gl_view 2"))
                tests.append((tview3, "Test ViewPlatform.gl_view 3"))
                tests.append((tview4, "Test ViewPlatform.gl_view 4"))
                tests.append((tview5, "Test ViewPlatform.gl_view 5"))

                TestContext.test_results = tests

            def test_projection(self, fovy, aspect, zNear, zFar):
                """Perform test on the projection matrix computation"""

                GL.glMatrixMode(GL.GL_PROJECTION)
                GL.glLoadIdentity()
                GLU.gluPerspective(RAD_TO_DEG * fovy, aspect, zNear, zFar)
                matrix1 = GL.glGetDoublev(GL.GL_PROJECTION_MATRIX)

                vp = dasty.core.ViewPlatform()
                vp.set_frustum(fovy, aspect, zNear, zFar)
                matrix2 = vp.gl_projection

                m = (matrix1 - matrix2)
                dif_projection = numpy.sum(m*m)
                return dif_projection < 0.001

            def test_view(self, position, orientation):
                """Perform test on the view matrix computation"""

                vp = dasty.core.ViewPlatform()
                vp.set_position(position)
                vp.set_orientation(orientation)
                matrix2 = vp.gl_view

                GL.glMatrixMode(GL.GL_MODELVIEW)
                GL.glLoadIdentity()
                vp.gl_apply()
                matrix1 = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)

                m = (matrix1 - matrix2)
                dif_view = numpy.sum(m*m)

                if dif_view >= 0.001:
                    print "ERROR: GL_MATRIX != VP_MATRIX"
                    print_format("GL_MATRIX", matrix1, "%+1.2f")
                    print_format("VP_MATRIX", matrix2, "%+1.2f")
                return dif_view < 0.001

        GLUT.glutInit(sys.argv)
        context = TestContext()
        GLUT.glutMainLoopEvent()
        for result, name in TestContext.test_results:
            assert result == True, name

if __name__ == '__main__':
    unittest.main()
