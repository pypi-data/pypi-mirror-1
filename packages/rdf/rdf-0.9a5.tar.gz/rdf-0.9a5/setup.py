from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

import rdf as package

setup(
    name = package.__name__,
    version = package.__version__,
    description = package.__doc__.split("\n")[0],
    long_description = package.__doc__,

    author = "Daniel 'eikeon' Krech",
    author_email = "eikeon@eikeon.com",
    maintainer = "Daniel 'eikeon' Krech",
    maintainer_email = "eikeon@eikeon.com",
    url = "http://rdflib.net/",
    license = "http://rdflib.net/latest/LICENSE",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python",
                   "License :: OSI Approved :: BSD License",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   "Operating System :: OS Independent",
                   "Natural Language :: English",
                   ],
    packages = find_packages(),

    tests_require = ["nose>=0.10.1", 'rdflib>=3.0.0a3'],

    test_suite = 'nose.collector',

    )

