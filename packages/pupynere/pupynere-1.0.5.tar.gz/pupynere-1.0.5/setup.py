RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 5 - Production/Stable
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '1.0.5'

setup(
        name='pupynere',
        version=version,
        description="NetCDF file reader and writer.",
        long_description="""\
Pupynere is a Python module for reading and writing NetCDF files,
using the same API as Scientific.IO.NetCDF and pynetcdf. It depends only
on Numpy, so you don't need to have the NetCDF library installed.

Changelog:

1.0.5
  Added the option to open files without using mmap, since mmap can't
  handle huge files on Windows.

1.0.4
  Fixed packing of dimensions when writing a file. The order was being
  read from a dictionary (essentially unordered), instead of from the list
  with the proper order.

1.0.3
  Fixed bug so that it can write scalar variables.

1.0.2
  Fixed broken 1.0.1, ``var.shape`` was returning the current number
  of records in the first dimension, breaking the detection of record
  variables.

1.0.1
  Changed the code to read the variable shape from the underlying
  data object.

1.0.0
  Initial stable release. Handles record arrays properly (using a single
  mmap for all record variables) and writes files.
""",
        classifiers=filter(None, classifiers.split("\n")),
        keywords='netcdf data array math',
        author='Roberto De Almeida',
        author_email='roberto@dealmeida.net',
        url='http://dealmeida.net/2008/07/14/pupynere',
        download_url = "http://cheeseshop.python.org/packages/source/p/pupynere/pupynere-%s.tar.gz" % version,
        license='MIT',
        py_modules=['pupynere'],
        include_package_data=True,
        zip_safe=True,
        test_suite = 'nose.collector',
        install_requires=[
            'numpy',
        ],
        extras_require={
            'test': ['nose'],
        },
)
