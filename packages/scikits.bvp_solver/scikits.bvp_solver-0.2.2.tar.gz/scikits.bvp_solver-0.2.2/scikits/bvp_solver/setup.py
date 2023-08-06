"""
import setuptools
from numpy.distutils.core import setup, Extension


bvp_solverf = Extension(name = 'bvp_solverf', sources = ['lib/bvp_interface.pyf', 'lib/BVP_LA.f', 'lib/BVP_M.f90', 'lib/BVP_INTERFACE.f90'])
"""
#!/usr/bin/env python
from numpy.distutils.misc_util import Configuration

def configuration(parent_package='', top_path=None):
    config = Configuration('bvp_solver', parent_package, top_path)
    config.add_extension('bvp_solverf',
                         sources=['lib/bvp_interface.pyf',
                                  'lib/BVP_LA.f',
                                  'lib/BVP_M.f90',
                                  'lib/BVP_INTERFACE.f90'])
    return config
