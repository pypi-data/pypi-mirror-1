"""Define the Phong material class.

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.
"""

import dasty.core

class Phong(dasty.core.Material):
    """Phong material.

    Attributes are:
    diffuse_color -- list of 4 floats (red, green, blue, alpha)
    specular_color -- list of 4 floats (red, green, blue, alpha)
    specular_exponent -- 1 float
    """

    def __init__(self):
        dasty.core.Material.__init__(self)
        self.diffuse_color = (0.0, 0.0, 0.0, 1.0)
        self.specular_color = (0.0, 0.0, 0.0, 1.0)
        self.specular_exponent = 16.0
