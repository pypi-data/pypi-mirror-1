"""Define the ViewPlatform class

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.

"""
# No need to reimplement everything, re-use a few OpenGLContext classes.
import OpenGLContext.viewplatform
from dasty.core.Quaternion import Quaternion
import numpy

class ViewPlatform(object):
    """Mobile Viewing Platform

    The ViewPlatform is, loosely speaking, a camera which sets up the projection
    and model-view matrices for a scene.

    Attributes:
    frustum -- OpenGL-friendly storage of frustum values,
            (field of view, aspect ratio, near, far)
    position -- object-space position of the viewing platform, a four-component
                array
    quaternion -- quaternion representing the current view-orientation for the
                viewing platform
    gl_projection -- projection matrix (4x4 numpy matrix of floats)
    gl_view -- view matrix (4x4 numpy matrix of floats)

    """

    def __init__(self, position=(0, 0, 10), orientation=(0, 1, 0, 0),
                 fieldOfView=1.0471975511965976, aspect=1.0,
                 near=0.01, far=1000):
        """Initialize the ViewPlatform

        position -- 3D coordinate position of the "camera"
        orientation -- VRML97-style 4-component orientation, that is, axis as
                   three floats followed by radian rotation as a single float.
        fieldOfView -- radian angle field of view
        aspect -- float aspect ratio of window, width/height
        near -- object-space distance to the near clipping plane
        far -- object-space distance to the far clipping plane

        """
        self._vp = OpenGLContext.viewplatform.ViewPlatform()
        self.gl_projection = numpy.identity(4, 'f')
        self.gl_view = numpy.identity(4, 'f')
        self.set_position(position)
        self.set_orientation(orientation)
        self.set_frustum(fieldOfView, aspect, near, far)

    def gl_apply(self):
        """Perform the actual view-platform setup during rendering

        This is really quite a trivial function, given the amount of setup
        that's been done before-hand. The gluPerspective function takes care
        of the perspective-matrix setup, while self.quaternion (Quaternion)
        takes care of the rotation, and positioning is a simple call to
        glTranslate.

        See:
            gluPerspective

        """
        self._vp.render()

    def set_frustum(self, fieldOfView=1.5707963267948966, aspect=1, near=0.01, far=1000):
        """Set the current frustum values for the "camera"

        fieldOfView -- radian angle field of view
        aspect -- float aspect ratio of window, width/height
        near -- object-space distance to the near clipping plane
        far -- object-space distance to the far clipping plane

        """
        self.frustum = (fieldOfView, aspect, near, far)
        self._vp.setFrustum(fieldOfView, aspect, near, far)
        self._compute_projection()

    def set_orientation(self, orientation):
        """Set the current "camera orientation"

        Keyword arguments:
        orientation -- VRML97-style 4-component orientation, that is, axis as
                    three floats followed by radian rotation as a single float

        Alternately, a dasty.core.Quaternion instance representing the
        orientation.  Note that the orientation will likely be 180 degrees
        from what you expect, this method reverses the rotation value when
        passed a VRML97-style orientation.

        """
        self._vp.setOrientation(orientation)
        self._compute_view()

    def set_position(self, position):
        """Set the current "camera position"
        
        position -- 3D coordinate position to which to teleport the "camera"

        """
        self._vp.setPosition(position)
        self._compute_view()

    def set_viewport(self, w, h):
        """Set the current viewport/window dimensions
         
        w,h -- integer width and height (respectively) of the window
          
        This method simply updates the frustum attribute to reflect the new
        aspect ratio.

        """
        self._vp.setViewport(w, h)

    def _compute_projection(self):
        # Compute projection matrix
        fovy,aspect,zNear,zFar = self.frustum
        f = 1.0 / numpy.tan(fovy / 2.0)

        gl_projection = self.gl_projection
        gl_projection *= 0.0 # Set everything to zero
        gl_projection[0,0]  = f / aspect
        gl_projection[1,1]  = f
        gl_projection[2,2]  = (zFar + zNear) / (zNear - zFar)
        gl_projection[3,2]  = (2.0 * zFar * zNear) / (zNear - zFar)
        gl_projection[2,3]  = -1.0

    def _compute_view(self):
        x,y,z,r = self.quaternion.XYZR()
        cos_r = numpy.cos(r)
        sin_r = numpy.sin(r)
        one_minus_cos_r = 1.0 - cos_r

        gl_view = self.gl_view
        gl_view[0,0] = one_minus_cos_r * x * x + cos_r
        gl_view[1,0] = one_minus_cos_r * x * y - sin_r * z
        gl_view[2,0] = one_minus_cos_r * x * z + sin_r * y

        gl_view[0,1] = one_minus_cos_r * y * x + sin_r * z
        gl_view[1,1] = one_minus_cos_r * y * y + cos_r
        gl_view[2,1] = one_minus_cos_r * y * z - sin_r * x

        gl_view[0,2] = one_minus_cos_r * z * x - sin_r * y
        gl_view[1,2] = one_minus_cos_r * z * y + sin_r * x
        gl_view[2,2] = one_minus_cos_r * z * z + cos_r

        r = -r
        q = Quaternion.from_XYZR(x,y,z,r)
        gl_view[3,0:3] = (q * -self.position)[0:3]
        gl_view[3,3]   = 1.0

    def __getattr__(self, name):
        return self._vp.__dict__[name]

