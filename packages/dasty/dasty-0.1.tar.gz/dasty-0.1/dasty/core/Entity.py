"""Define the Entity class

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.
"""

class Entity(object):
    """Instance of an MMM.

       Normally contains instanciation parameters so that the drawing of an
       Entity will call the drawing of its model with appropriate parameters.

       Attributes:
       mmm -- the MMM associated with the Entity
       aabbox -- Axis Aligned Bounding Box (xmin, max, ymin, ymax, zmin, zmax)
       material_id -- ID of associated material
    """

    def __init__(self, name, mmm):
        """Initialize the Entity associated with given MMM.

        Keyword arguments:
        name -- a String identifier for the entity
        mmm -- template MMM to associate with the entity

        """
        self.name = name
        self.mmm = mmm
        self.aabbox = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        self.material_id = None

    def gl_draw(self, viewplatform, wsize):
        """Draw to OpenGL active context.

        Keyword arguments:
        viewplatform -- a dasty.core.ViewPlatform defining the user camera
        wsize -- size in pixels of the aabbox projected on screen (w,h)

        Note: default implementation just call the mmm's gl_draw method.

        """
        self.mmm.gl_draw(viewplatform, wsize)

    def compile(self):
        """Setup the entity"""
        pass
