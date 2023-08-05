"""Convert COARDS time specification to a datetime object.

This function converts between a given COARDS time specification and a
Python datetime object, which is much more useful. 
"""

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

__author__ = "Roberto De Almeida <rob@pydap.org>"
__version__ = (0,1,1)

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

version = '.'.join([str(_) for _ in __version__])

# Generate description and long_description.
doclines = __doc__.split("\n")

setup(
    name = "coards",
    version = version,
    packages = find_packages(),

    # Requirements.
    install_requires = [
    ],

    entry_points = {
    },

    zip_safe = True,

    # Metadata for PyPI.
    author = "Roberto De Almeida",
    author_email = "rob@pydap.org",

    description = doclines[0],
    long_description = "\n".join(doclines[2:]),
    license = "MIT",
    keywords = "data time",
    url = "http://pydap.org/",
    download_url = "http://cheeseshop.python.org/packages/source/c/coards/coards-%s.tar.gz" % version,
    platforms = ['any'],
    classifiers = filter(None, classifiers.split("\n")),
)
