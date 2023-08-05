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

version = '0.1.1'

setup(name='arrayterator',
      version=version,
      description="Buffered iterator for big arrays.",
      long_description="""\
This class creates a buffered iterator for reading big arrays in small
contiguous blocks. The class can be used with any object that supports
multidimensional slices and a copy() method, like variables from
Scientific.IO.NetCDF, pynetcdf and numpy.array.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='data array math',
      author='Rob De Almeida',
      author_email='rob@pydap.org',
      url='http://dealmeida.net/projects/arrayterator',
      download_url = "http://cheeseshop.python.org/packages/source/a/arrayterator/arrayterator-%s.tar.gz" % version,
      license='MIT',
      #packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      py_modules=['arrayterator'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
      
