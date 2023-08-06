#! /usr/bin/env python

"""PyHepMC: a Python interface to the HepMC high-energy physics event record API"""

## Get setuptools
import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, Extension

longdesc = """This is a simple SWIG wrapper on the main classes of the HepMC event
simulation representation, making it possible to create, read and manipulate HepMC
events from Python code.
"""

## Setup definition
setup(name = 'pyhepmc',
      version = '0.3.1',
      #include_package_data = True,
      ## SWIG support currently blocks use of -outdir. Aargh!
      ext_modules=[Extension('_hepmc', ['./hepmc.i'],
                            swig_opts=['-c++', '-I/home/andy/heplocal/include'],
                            #swig_opts=['-c++', '-I/home/andy/heplocal/include', '-outdir .'],
                            include_dirs=['/home/andy/heplocal/include'],
                            library_dirs=['/home/andy/heplocal/lib'],
                            libraries=['HepMC'])],
#       ext_modules=[Extension('_hepmc', ['./hepmc.i'],
#                              swig_opts=['-c++', '-I/home/andy/heplocal/include', '-outdir .'],
#                              include_dirs=['/home/andy/heplocal/include'],
#                              library_dirs=['/home/andy/heplocal/lib'],
#                              libraries=['HepMC'])],      
      py_modules = ['hepmc'],

      author = ['Andy Buckley'],
      author_email = 'andy@insectnation.org',
      #url = 'http://projects.hepforge.org/professor/',
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
