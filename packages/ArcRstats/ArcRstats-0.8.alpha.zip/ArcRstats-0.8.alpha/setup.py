"""Installs ArcRstats using distutils

Run:
    python setup.py install

to install this package.
"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

classifiers=[
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Natural Language :: English",
    "Operating System :: Microsoft",
    "Programming Language :: Python",
    "Topic :: Scientific/Engineering :: GIS",
    "Topic :: Scientific/Engineering :: Bio-Informatics",
    "Topic :: Scientific/Engineering :: Information Analysis",
    "Topic :: Scientific/Engineering :: Mathematics", 
]

setup(
    name = "ArcRstats",
    version = "0.8.alpha",
    description = "geostatistical functions linking ESRI ArcGIS to R statistics packages",
    long_description = "ArcRstats - produces multivariate habitat prediction rasters using ArcGIS and the open-source R statistical package for implementing classification and regression (CART), generalized linear models (GLM) and generalized additive models (GAM).",
    keywords = "GIS, geographical information systems; statistics; R; GLM, generalized linear model; CART, classification and regression trees; GAM, generalized additive model; connectivity; graph theory; landscape ecology; conservation biology",
    author="Ben Best",
    author_email="bbest@duke.edu",
    url="http://www.env.duke.edu/geospatial/software/",
    license="GNU",
    classifiers=classifiers,
    packages = find_packages(),
    package_data = {'': ['*.pdf', '*.txt', '*.rst', '*.R'],},
)