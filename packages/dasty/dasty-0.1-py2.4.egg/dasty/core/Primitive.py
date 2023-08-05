"""Define the Primitive class

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.
"""

class Primitive(object):
    """An object having ability to draw itself.

    Attributes:
    aabbox -- Axis Aligned Bounding Box (xmin,xmax,ymin,ymax,zmin,zmax)

    """

    def __init__(self):
        self.aabbox = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    def compile(self):
        """Perform necessary precomputations"""
        pass

    def gl_draw(self, viewplatform, wsize):
        """Draw the primitive to OpenGL active context.

        Keyword arguments:
        viewplatform -- a ViewPlatform defining the user camera
        wsize -- size in pixels of the aabbox projected on screen (w,h)

        """
        pass
