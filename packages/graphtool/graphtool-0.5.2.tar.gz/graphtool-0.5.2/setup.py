#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name = "graphtool",
    version = "0.5.2",
    description = "CMS Common Graphing Package.",
    author = "Brian Bockelman",
    author_email = "bbockelm@math.unl.edu",
    package_dir = {'graphtool.static_content': 'static_content', 'graphtool': 'src/graphtool'},
    packages = find_packages('src') + ["graphtool.static_content"],
    include_package_data = True,

    classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'Programming Language :: Python',
          'Natural Language :: English',
          'Operating System :: POSIX'
    ],

    dependency_links = ['http://www.pythonware.com/products/pil/'],
    install_requires=["CherryPy<=3.1", "matplotlib<=0.90.1", "numpy", "PIL"],
    
    #package_data = {"graphtool_static_content":["*"], "graphtool_example":["*"]}
)
