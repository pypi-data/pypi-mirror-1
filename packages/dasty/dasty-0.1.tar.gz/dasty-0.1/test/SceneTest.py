"""Unit test for dasty.core.Scene.

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.
"""

import dasty
import unittest

class ConsolePrimitive(dasty.core.Primitive):
    """Primitive used to test things"""

    def __init__(self, name):
        dasty.core.Primitive.__init__(self)
        self.name = name

    def __str__(self):
        return "Primitive:%s" % self.name

SHIFT_WIDTH = 1


def mmm_node_to_str(node, level):
    """Display a node to the console for debugging purposes."""
    ret = (' ' * level) + ' entity.name = "'+node.entity.name+'" {\n'
    ret += mmm_to_str(node.entity.mmm, level+SHIFT_WIDTH)
    if len(node.child_nodes) > 0:
        ret += (' ' * (level+SHIFT_WIDTH)) + ' "' \
            + node.entity.name + '" childs {\n'
        for child_node in node.child_nodes:
            ret += mmm_node_to_str(child_node, level+SHIFT_WIDTH*2)
        ret += ' ' * (level+SHIFT_WIDTH) + " }\n"
    ret += ' ' * level + ' }\n'
    return ret


def mmm_to_str(mmm, level=0):
    """Display the decomposition to the console for debugging purposes"""
    ret = ''
    if not mmm.primitive is dasty.core.MMM.EMPTY_PRIMITIVE:
        ret += (' ' * level) + " mmm.primitive = " + str(mmm.primitive) + "\n"
    if len(mmm.decomposition_roots) > 0:
        ret += (' ' * level) + " mmm.graph = {\n"
        for node in mmm.decomposition_roots:
            ret += mmm_node_to_str(node, level+SHIFT_WIDTH)
        ret += (' ' * level) + " }\n"
    return ret

class SceneTest(unittest.TestCase):
    """Launch a simple test."""

    def setUp(self):
        """Build a test scene"""
        # Build needed primitives
        mesh_trunk = ConsolePrimitive("mesh_trunk")
        mesh_branch = ConsolePrimitive("mesh_branch")
        mesh_small_branch = ConsolePrimitive("mesh_small_branch")
        billboard_apple_tree = ConsolePrimitive("billboard_apple_tree")

        # Build the MMMs
        apple_trunk = dasty.core.MMM()
        apple_trunk.primitive = mesh_trunk

        apple_branch = dasty.core.MMM()
        apple_branch.primitive = mesh_branch

        small_branch = dasty.core.MMM()
        small_branch.primitive = mesh_small_branch

        apple_tree = dasty.core.MMM()
        apple_tree.primitive = billboard_apple_tree

        # Instanciate entities
        my_apple_tree = dasty.core.Entity("apple tree", apple_tree)
        my_trunk = dasty.core.Entity("trunk", apple_trunk)
        my_branch1 = dasty.core.Entity("branch1", apple_branch)
        my_branch2 = dasty.core.Entity("branch2", apple_branch)
        my_branch3 = dasty.core.Entity("branch3", small_branch)

        # Create the decompotion tree of the apple tree
        apple_tree.add_to_decomposition(my_trunk)
        apple_tree.add_to_decomposition(my_branch1, parent_name="trunk")
        apple_tree.add_to_decomposition(my_branch2, parent_name="trunk")
        apple_tree.add_to_decomposition(my_branch3, parent_name="branch2")

        # Add an apple tree to the scene
        self.scene = dasty.core.Scene()
        self.scene.add_to_decomposition(my_apple_tree)

    def runTest(self):
        """Check content of the test scene"""
        what_result_should_be = \
            ' mmm.graph = {\n' + \
            '  entity.name = "apple tree" {\n' + \
            '   mmm.primitive = Primitive:billboard_apple_tree\n' + \
            '   mmm.graph = {\n' + \
            '    entity.name = "trunk" {\n' + \
            '     mmm.primitive = Primitive:mesh_trunk\n' + \
            '     "trunk" childs {\n' + \
            '      entity.name = "branch1" {\n' + \
            '       mmm.primitive = Primitive:mesh_branch\n' + \
            '      }\n' + \
            '      entity.name = "branch2" {\n' + \
            '       mmm.primitive = Primitive:mesh_branch\n' + \
            '       "branch2" childs {\n' + \
            '        entity.name = "branch3" {\n' + \
            '         mmm.primitive = Primitive:mesh_small_branch\n' + \
            '        }\n' + \
            '       }\n' + \
            '      }\n' + \
            '     }\n' + \
            '    }\n' + \
            '   }\n' + \
            '  }\n' + \
            ' }\n'

        assert mmm_to_str(self.scene) == what_result_should_be

if __name__ == "__main__":
    unittest.main()
