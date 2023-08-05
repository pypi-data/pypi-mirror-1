from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

# TODO: this is not working since it doesn't look like the
# setup_requires get installed before the import gets hit.
#
# from hypercode import __version__

setup(
    name = 'hypercode',
    version = "0.2a2",
    description = "This is a pure Python package for working with RDF.",
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
    long_description = \
    """
    """,

    packages = find_packages(),
    py_modules = ['hypercode'],

    setup_requires = ['rdflib>=3.0.0a3'],
    install_requires = ['rdflib>=3.0.0a3'],

    tests_require = ["nose==0.10.1"],

    test_suite = 'nose.collector',

    )

