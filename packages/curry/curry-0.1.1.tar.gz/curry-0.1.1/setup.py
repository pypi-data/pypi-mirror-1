__version__ = '0.1.1'

import os
import sys

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

version = sys.version_info[:3]
test_suite = "curry.tests.base"

setup(
    name="curry",
    version=__version__,
    description="Partial application of Python methods.",
    long_description="\n\n".join((README, CHANGES)),
    classifiers=[
       "Development Status :: 3 - Alpha",
       "Intended Audience :: Developers",
       "Programming Language :: Python",
       "Topic :: Internet :: WWW/HTTP",
       "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
       "Topic :: Internet :: WWW/HTTP :: WSGI",
      ],
    keywords='cooking partial curry optimization ast',
    author="Malthe Borch",
    author_email="mborch@gmail.com",
    license='BSD',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data=True,
    zip_safe=False,
    test_suite=test_suite,
    )

