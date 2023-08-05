"""Procedures to study fluids on Python, focused for oceanography, meteorology and related sciences.

Fluid is a set of procedures to study fluids, focused for 
ocean and atmosphere analysis.

It's able to estimate/convert basic variables such as mixing ratio, 
saturation vapor pressure and air viscosity, and estimate heat fluxes 
between air-sea interface.

Great structure modifications are expected in upcoming versions.

Until version 1.0 I'll try to keep backward compatibility, but I 
can't guarantee.

I started to develop this package while being funded by SAAC-IAI, CAPES and FAPESP.
"""
from setuptools import setup, find_packages

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Science/Research
Intended Audience :: Developers
Intended Audience :: Education
License :: OSI Approved :: MIT License 
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Education
Topic :: Software Development :: Libraries :: Python Modules
"""

from distutils.core import setup

doclines = __doc__.split("\n")

setup(name = "fluid",
      version = '0.1.5',
      description = doclines[0],
      long_description = "\n".join(doclines[2:]),
      author = "Guilherme Castelao and Roberto de Almeida",
      author_email = "guilherme@castelao.net and roberto@dealmeida.net",
      url = "http://fluid.oceanografia.org/",
      download_url = "http://fluid.oceanografia.org/download/fluid-0-1-5-tar.gz",
      packages = ['fluid', 'fluid.common','fluid.ocean', 'fluid.atmosphere', 'fluid.interaction'],
      license = 'MIT',
      platforms = ["any"],
      classifiers = filter(None, classifiers.split("\n")),
     )
