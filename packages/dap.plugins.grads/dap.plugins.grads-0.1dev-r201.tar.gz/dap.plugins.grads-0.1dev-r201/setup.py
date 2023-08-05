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

setup(name='dap.plugins.grads',
      version=version,
      description="GrADS/GRIB plugin for pydap server",
      long_description="""\
This is a plugin for serving data in a pydap server from GrADS/GRIB files.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/plugins/grads#egg=dap.plugins.grads-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='grads grib dap opendap dods data',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/plugins/grads.html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['dap.plugins'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          #'Numeric',
          #'cdms',
          'dap[server]>=2.2.4',
          'arrayterator>=0.2.4',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [dap.plugin]
      main = dap.plugins.grads
      """,
      )
      
