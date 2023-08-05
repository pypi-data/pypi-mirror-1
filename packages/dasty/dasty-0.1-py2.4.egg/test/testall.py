#!/usr/bin/python

"""Launch all tests from the dasty/tests directory.

Author: Jean-Christophe Hoelt <hoelt@irit.fr>
Copyright (c) 2007, IRIT-CNRS

This file is released under the CECILL-C licence.

"""

from test.SceneTest import SceneTest
from test.ViewPlatformTest import ViewPlatformTest
import unittest

if __name__ == "__main__":
    unittest.main()
