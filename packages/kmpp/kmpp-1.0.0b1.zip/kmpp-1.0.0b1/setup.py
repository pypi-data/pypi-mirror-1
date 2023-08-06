#! /usr/bin/env python
from distutils.core import setup, Extension
import numpy

module1 = Extension(
    'kmpp',
    include_dirs = [numpy.get_include()],
    sources = ['kmppmodule.cpp', 'KMeans.cpp', 'KmUtils.cpp', 'KmTree.cpp'])

setup (name = 'kmpp',
       version = '1.0.0b1',
       description = 'Contains kmeans plus plus',
       author = 'David Arthur (Python wrapper: Per Rosengren)',
       author_email = 'darthur@gmail.com',
       url = 'http://www.stanford.edu/~darthur/kmpp.zip',
       license = 'Copyright David Arthur',
       ext_modules = [module1],
       py_modules = ['kmpp_test'])
