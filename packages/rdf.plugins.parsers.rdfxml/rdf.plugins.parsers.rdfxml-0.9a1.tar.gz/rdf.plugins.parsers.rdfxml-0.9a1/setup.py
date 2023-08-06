from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

import rdfxml as package


setup(
    name = "rdf.plugins.parsers.rdfxml",
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


    py_modules = ["rdfxml"],

    install_requires = ['rdf>=0.9a4'],

    tests_require = ["nose==0.10.1"],

    test_suite = 'nose.collector',

    )
