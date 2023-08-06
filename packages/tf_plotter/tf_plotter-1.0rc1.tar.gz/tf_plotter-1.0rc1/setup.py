#!/usr/bin/env python

import warnings
warnings.filterwarnings('ignore')

from distutils.core import setup

from os.path import abspath, dirname
from sys import path
path.insert(0, '%s/src' % dirname(abspath(__file__)))

import tf_plotter

setup(
    name=tf_plotter.__name__,
    version=tf_plotter.__version__,
    license=tf_plotter.__license__,
    description=tf_plotter.__description__,
    author=tf_plotter.__author__,
    author_email=tf_plotter.__email__,
    url=tf_plotter.__url__,
    packages=[tf_plotter.__name__],
    package_dir={
        tf_plotter.__name__: 'src/%s' % tf_plotter.__name__
    },
    scripts=['src/tf-plotter'],
    
    # we needs controlsystems-1.0rc3, but distutils don't accept
    requires=['controlsystems (>=1.0)', 'matplotlib']
)
