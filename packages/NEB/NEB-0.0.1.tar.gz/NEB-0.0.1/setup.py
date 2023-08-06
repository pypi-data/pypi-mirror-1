"""\
Top level namespace project for from New England Biolabs
"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, Extension

setup(
    name = "NEB",
    version = "0.0.1",
    license = "MIT",
    author = "Paul J. Davis",
    author_email = "davisp@neb.com",
    description = "Namespace package for NEB projects.",
    long_description = __doc__,
    url = "http://github.com/neb",
    download_url = "http://github.com/neb/neb.git",
    zip_safe = True,

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    setup_requires = [
        'setuptools>=0.6c8',
    ],

    packages = [
        'neb'
    ],
)
