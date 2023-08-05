"""Buffered iterator for big arrays.

This class creates a buffered iterator for reading big arrays in small
contiguous blocks. The class can be used with any object that supports
multidimensional slices and a copy() method, like variables from
Scientific.IO.NetCDF, pycdf, Numeric.array and numarray.array.
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

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import arrayterator
version = '.'.join([str(_) for _ in arrayterator.__version__])

# Generate description and long_description.
doclines = __doc__.split("\n")

setup(
    name = "arrayterator",
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
    keywords = "data array math",
    url = "http://pydap.org/",
    download_url = "http://cheeseshop.python.org/packages/source/a/arrayterator/arrayterator-%s.tar.gz" % version,
    platforms = ['any'],
    classifiers = filter(None, classifiers.split("\n")),
)
