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

version = '1.0.1'

setup(
        name='pupynere',
        version=version,
        description="NetCDF file reader and writer.",
        long_description="""\
Pupynere is a Python module for reading and writing NetCDF files,
using the same API as Scientific.IO.NetCDF and pynetcdf. It depends only
on Numpy, so you don't need to have the NetCDF library installed.
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
