"""Define the Primitive class

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.
"""

from dasty.core.MMM import MMM

class Scene(MMM):
    """Objects and materials of the scene"""

    def __init__(self):
        MMM.__init__(self)

    def add_entity(self, entity):
        self.add_to_decomposition(entity)
