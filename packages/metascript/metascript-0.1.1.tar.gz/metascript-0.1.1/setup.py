#!/usr/bin/env python

from distutils.core import setup, Extension

setup(name="metascript",
      version="0.1.1",
      description="Metascript retrieval and processing",
      author="Michael Hoffman",
      author_email="hoffman@ebi.ac.uk",
      url="http://www.ebi.ac.uk/~hoffman/software/metascript/",
      classifiers=["Development Status :: 3 - Alpha",
                   "Intended Audience :: Science/Research",
                   "License :: Other/Proprietary License",
                   "Natural Language :: English",
                   "Programming Language :: Python",
                   "Topic :: Scientific/Engineering :: Bio-Informatics"],
      packages=['metascript'],
      package_dir={'metascript': 'lib'},
      ext_package="metascript",
      ext_modules=[Extension('_glob',
                             sources=['lib/_glob.c'],
                             extra_compile_args=["-std=c99"])],
      scripts = ['scripts/pairup',
                 'scripts/get_metascripts',
                 'scripts/exons_in_introns']
      )
