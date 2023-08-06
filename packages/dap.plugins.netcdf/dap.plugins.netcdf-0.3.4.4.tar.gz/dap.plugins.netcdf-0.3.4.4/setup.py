# If true, then the svn revision won't be used to calculate the
# revision (set to True for real releases)
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
Topic :: Internet
Topic :: Scientific/Engineering
Topic :: Software Development :: Libraries :: Python Modules
"""

version = '0.3.4.4'

setup(name='dap.plugins.netcdf',
      version=version,
      description="netCDF plugin for pydap server",
      long_description="""\
This is a plugin for serving data in a pydap server from netCDF 3
files. It works either with the pynetcdf module or with pupynere,
an experimental pure Python netCDF reader.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/plugins/netcdf#egg=dap.plugins.netcdf-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='netcdf dap opendap dods data',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/plugins/netcdf.html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['dap.plugins'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'dap[server]>=2.2.6',
          'pupynere>=0.2.4',
          'arrayterator>=0.2.8',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [dap.plugin]
      main = dap.plugins.netcdf
      """,
      )
      
