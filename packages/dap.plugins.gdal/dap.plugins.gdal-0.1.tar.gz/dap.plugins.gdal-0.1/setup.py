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

version = '0.1'

setup(name='dap.plugins.gdal',
      version=version,
      description="GDAL plugin for pydap server",
      long_description="""\
This is a plugin for serving geospatial data in pydap using the
Geospatial Data Abstraction Library (GDAL).
      
The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/plugins/gdal#egg=dap.plugins.gdal-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='gdal dap opendap dods data',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/plugins/gdal.html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['dap.plugins'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          #'gdal',
          'dap[server]>=2.2.5.4',
          'arrayterator>=0.2.6',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [dap.plugin]
      main = dap.plugins.gdal
      """,
      )
      
