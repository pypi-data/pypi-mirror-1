#! /usr/bin/env python

"""mcview: a 3D / graph event viewer for high-energy physics event simulations"""

## Get setuptools
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

longdesc = """mcview uses the Python wrapper for HepMC to load and view HepMC
events as 3D final-state representations in (log-)momentum space, and to dump
the graph structure to PDF and graphviz formats.
"""

## Setup definition
setup(name = 'mcview',
      version = "0.4.0",
      #include_package_data = True,
      install_requires = ['pyhepmc>=0.3', 'pydot'], # 'visual'/'vpython'
      scripts = ['mcview'],
      author = ['Andy Buckley'],
      author_email = 'andy@insectnation.org',
      #url = 'http://projects.hepforge.org/professor/',
      description = 'A 3D / graph event viewer for high-energy physics event simulations',
      long_description = longdesc,
      keywords = 'generator montecarlo simulation data hep physics particle',
      license = 'GPL',
      classifiers = ['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Science/Research',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python',
                   'Topic :: Scientific/Engineering :: Physics']
      )
