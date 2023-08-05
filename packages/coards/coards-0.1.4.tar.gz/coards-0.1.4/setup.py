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

version = '0.1.4'

setup(name='coards',
      version=version,
      description="Convert COARDS time specification to a datetime object.",
      long_description="""\
This module converts between a given COARDS time specification and a
Python datetime object, which is much more useful. Suppose you have an
Array of values [1,2,3] and units "days since 1998-03-01 12:00:00"::

    >>> a = [1, 2, 3]
    >>> units = 'days since 1998-03-01 12:00:00'
    >>> b = [parseUdunits(value, units) for value in a]
    >>> print b[0].year
    1998
    >>> b[1] > b[0]
    True
    >>> print b[1] - b[0]
    1 day, 0:00:00

The list 'b' now contains objects which can be compared and manipulated in
a consistent way.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/coards#egg=coards-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='data time coards netcdf',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://dealmeida.net/projects/coards',
      download_url = "http://cheeseshop.python.org/packages/source/c/coards/coards-%s.tar.gz" % version,
      license='MIT',
      py_modules=['coards'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
