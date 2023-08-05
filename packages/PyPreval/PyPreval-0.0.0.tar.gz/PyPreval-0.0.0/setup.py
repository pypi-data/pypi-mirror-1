'''
This package provides an object prevalence service.
'''

import ez_setup
ez_setup.use_setuptools()

__version__                 = '0.0.0'
__description__             = 'object prevalence service'
__long_description__        = __doc__
__author__                  = 'Andreas Kostyrka'
__author_email__            = 'andreas@kostyrka.org'
__maintainer__              = __author__
__maintainer_email__        = __author_email__
__classifiers__             = [
    "Development Status :: 3 - Alpha",
    "Topic :: Database :: Database Engines/Servers",
    "Programming Language :: Python",
    "Operating System :: OS Independent",
    "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
    "Intended Audience :: Developers",
    ]

from setuptools import setup, find_packages

setup(
    name                    = 'PyPreval',
    version                 = __version__, 
    description             = __description__,
    long_description        = __long_description__,
    author                  = __author__,
    author_email            = __author_email__,
    maintainer              = __maintainer__,
    maintainer_email        = __maintainer_email__,
    classifiers             = __classifiers__,
    zip_safe                = True,
    include_package_data    = True,
    packages                = find_packages(),
    platforms               = ['any'],
    )
