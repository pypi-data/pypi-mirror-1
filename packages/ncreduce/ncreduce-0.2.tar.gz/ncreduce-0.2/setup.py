# -*- coding: utf-8 -*-
from numpy.distutils.core import setup, Extension

ncreduce = Extension('ncreduce', sources = ['ncreduce/reduce.cpp', 'ncreduce/numpy_utils.hpp'], extra_compile_args=['-Wno-sign-compare'])

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Topic :: Scientific/Engineering',
    ]

setup (name = 'ncreduce',
       version = '0.2',
       description = 'Fast reduce operations for numpy arrays',
       author='Luis Pedro Coelho',
       author_email='lpc@cmu.edu',
       license='GPL (v2 or later)',
       url='http://luispedro.org/software/ncreduce',
       classifiers=classifiers,
       ext_modules = [ncreduce],
       )
