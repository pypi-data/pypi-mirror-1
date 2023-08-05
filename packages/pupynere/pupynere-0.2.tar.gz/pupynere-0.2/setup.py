RELEASE = True

from setuptools import setup, find_packages
import sys, os

classifiers = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.2'

setup(name='pupynere',
      version=version,
      description="NetCDF file reader.",
      long_description="""\
Pupynere is a PUre PYthon NEtcdf REader. It allows read-access to netCDF
files using the same syntax as the Scientific.IO.NetCDF module. Even
though it's written in Python, the module is up to 40% faster than
Scientific.IO.NetCDF and pynetcdf.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/pupynere#egg=pupynere-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='netcdf data array math',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      #url='http://taoetc.org/6',
      download_url = "http://cheeseshop.python.org/packages/source/a/pupynere/pupynere-%s.tar.gz" % version,
      license='MIT',
      py_modules=['pupynere'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          #numpy,
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
