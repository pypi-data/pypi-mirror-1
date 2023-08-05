#!/usr/bin/env python
#-*- coding: utf-8 -*-
#from ez_setup import use_setuptools
#use_setuptools()

classifiers = """Development Status :: 4 - Beta
Environment :: Console
Environment :: X11 Applications
Environment :: X11 Applications :: GTK
Intended Audience :: Education
License :: OSI Approved :: GNU General Public License (GPL)
Natural Language :: Polish
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering :: Artificial Intelligence"""

#from setuptools import setup
from distutils.core import setup
setup(name='pyPSO',
      version='0.9.1',
      description='Implementation of Particle Swarm Optimalizator in python. \
      Toolkit with bunch of usefull tools.',
      long_description='Implementation of Particle Swarm Optimalizator in python. Toolkit with bunch of usefull tools.',
      platforms='Many',
      author='Damian Swistowski',
      author_email='dswistowski@gmail.com',
#      url='https://swistowski.czechowice.net/pypso/',
      keywords='Particle Swarm Optimalization PSO',
      license='GPL',
      scripts=['dane.py', 'psocommand.py', 'serie_komend.py',
      'psogui.py'],
      packages = ['pypso', 'pypso.ui', 'pypso.stats', 'pypso.widgets'],
#      install_requires = ['Numeric', 'pyGTK'],
#      install_requires = ['Numeric'],
      classifiers = classifiers.split('\n'),
      requires = ['Numeric'],
#      dependency_links = ['http://belnet.dl.sourceforge.net/sourceforge/gnuplot-py/gnuplot-py-1.7.zip',],
      )
