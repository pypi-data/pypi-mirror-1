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

version = '0.1.2'

setup(name='dap.responses.ddx',
      version=version,
      description="Experimental DDX response for pydap server",
      long_description="""\
An experimental implementation of the DDX response, based on the behavior of the official OPeNDAP server.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/responses/ddx#egg=dap.responses.ddx-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='xml ddx dap opendap dods data',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/responses/ddx.html',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['dap.responses'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'dap[server]>=2.2.6',
          'elementtree',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [dap.response]
      ddx = dap.responses.ddx
      """,
      )
      
