#!/usr/bin/env python

"""segtools: tools for interpreting and validating segmentations

LONG_DESCRIPTION
"""

__version__ = "0.1.0"

# Copyright 2008-2009 Michael M. Hoffman <mmh1@washington.edu>

import sys

# required for from __future__ import division, with_statement;
# relative imports
assert sys.version_info >= (2, 5, 1)

from ez_setup import use_setuptools
use_setuptools()

from setuptools import find_packages, setup

doclines = __doc__.splitlines()
name, short_description = doclines[0].split(": ")
long_description = "\n".join(doclines[2:])

url = "http://noble.gs.washington.edu/~mmh1/software/%s/" % name.lower()
download_url = "%s%s-%s.tar.gz" % (url, name, __version__)

dependency_links = ["http://noble.gs.washington.edu/~mmh1/software/genomedata/",
                    "http://pypi.python.org/packages/source/p/path.py/path-2.2.zip"]

classifiers = ["Natural Language :: English",
               "Programming Language :: Python"]

entry_points = """
[console_scripts]
segtools-feature-aggregation = segtools.feature_aggregation:main
segtools-label-transition = segtools.label_transition:main
segtools-length-distribution = segtools.length_distribution:main
segtools-nucleotide-frequency = segtools.nucleotide_frequency:main
segtools-overlap = segtools.overlap:main
segtools-signal-distribution = segtools.signal_distribution:main
segtools-html-report = segtools.html:main
"""
#segtools = segtools.validate_all:main

install_requires = ["genomedata", "numpy", "path", "rpy2", "textinput", "tables>=2.1"]

setup(name=name,
      version=__version__,
      description=short_description,
      author="Michael Hoffman",
      author_email="mmh1@washington.edu",
      maintainer="Orion Buske",
      maintainer_email="orion.buske@gmail.com",
      url=url,
      download_url=download_url,
      classifiers=classifiers,
      long_description=long_description,
      dependency_links=dependency_links,
      install_requires=install_requires,
      zip_safe=False,
      packages=find_packages("."),
      include_package_data=True,
      entry_points=entry_points
      )
