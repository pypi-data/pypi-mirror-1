#!/usr/bin/python

"""Dasty: data structure for multi-models and multi-resolutions 3D scenes

The Dasty data structure provides an advanced object-oriented application
programming interface for multi-models and multi-resolution 3D scene exchange.
It aims to provide a standardization for the describing of such scenes and an
implementations of a few useful classes.
"""

from setuptools import setup,find_packages

classifiers_ = """\
Development Status :: 3 - Alpha
Intended Audience :: Developers
License :: Other/Proprietary License
Programming Language :: Python
Topic :: Multimedia :: Graphics :: 3D Modeling
Topic :: Multimedia :: Graphics :: 3D Rendering
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: OS Independent
"""

doclines_ = __doc__.split("\n")

setup(name='dasty',
       version = '0.1',
       maintainer = "Vortex team, IRIT",
       maintainer_email = "hoelt@irit.fr",
       url = 'http://www.irit.fr/NatSim',
       license = "http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html",
       platforms = ["any"],
       description = doclines_[0],
       classifiers = filter(None, classifiers_.split("\n")),
       long_description = """Long description of the project...""",
       packages = find_packages(),
       )
