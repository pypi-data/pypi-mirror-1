"""Define the Material class

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.
"""

class Material(object):
    """Appearance of an entity"""

    def gl_bind(self):
        """Apply into the OpenGL context"""
        pass

    def gl_unbind(self):
        """Restore the OpenGL context to its previous state"""
        pass
