#! /usr/bin/env python

## Get setuptools
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, Extension

longdesc = """This is a simple SWIG wrapper on the main classes of the HepMC event
simulation representation, making it possible to create, read and manipulate HepMC
events from Python code.
"""

## SWIG support currently blocks use of -outdir. Aargh!
import os
ext = Extension('_hepmc', [os.path.abspath('./hepmc_wrap.cc')],
                #swig_opts=['-c++', '-I/mt/home/buckley/heplocal/include', '-outdir .'],
                include_dirs=['/mt/home/buckley/heplocal/include'],
                library_dirs=['/mt/home/buckley/heplocal/lib'],
                libraries=['HepMC'])

## Setup definition
setup(name = 'pyhepmc',
      version = '0.3.3',
      #include_package_data = True,
      ext_modules=[ext],
      py_modules = ['hepmc'],

      author = ['Andy Buckley'],
      author_email = 'andy@insectnation.org',
      description = 'A Python interface to the HepMC high-energy physics event record API',
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
