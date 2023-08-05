"""Define the MMM class

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.
"""

from dasty.core.Primitive import Primitive

class MMMNode:
    """Node of an MMM decomposition tree.

    Attributes:
    entity -- the associated dasty.Entity
    parent_node -- the parent MMMNode in the decomposition tree
    child_nodes -- child MMMNodes in the decomposition tree.

    """

    def __init__(self, entity, parent_node):
        self.entity = entity
        self.parent_node = parent_node
        self.child_nodes = []

    def add_child(self, child_node):
        """Add a child node"""
        self.child_nodes.append(child_node)

class MMM(object):
    """Multi-model, Multi-resolution, Multi-scale object.

       An MMM have:
         - a direct representation (Primitive), the way it is displayed at
           "base" resolution;
         - a decomposition tree, an acyclic tree of entities used for higher
           resolution display.

       Attributes:
       primitive -- the direct representation of the MMM (a Primitive)

    """

    EMPTY_PRIMITIVE = Primitive()

    def __init__(self):
        self.primitive = MMM.EMPTY_PRIMITIVE
        self.decomposition_roots = []
        self.decomposition_nodes = {}

    def add_to_decomposition(self, entity, parent_name=None):
        """Add the given entity to the decomposition tree and return its ID.

        Keyword arguments:
        entity -- entity to add
        parent_name -- mother node of this entity in the decomposition tree
                       (must be given if a tree structure is needed)

        """
        if parent_name is None:
            parent_node = None
        else:
            parent_node = self.decomposition_nodes[parent_name]

        node = MMMNode(entity, parent_node)
        self.decomposition_nodes[entity.name] = node

        if parent_name is None:
            self.decomposition_roots.append(node)
        else:
            node.parent_node = parent_node
            parent_node.add_child(node)

    def gl_draw(self, viewplatform, wsize):
        """Draw to OpenGL active context.

        Keyword arguments:
        viewplatform -- a ViewPlatform defining the user camera
        wsize -- size in pixels of the aabbox projected on screen (w,h)

        Note: default implementations calls primitive.gl_draw if available.

        """
        self.primitive.gl_draw(viewplatform, wsize)

