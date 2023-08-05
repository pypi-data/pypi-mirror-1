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

version = '0.3.1'

setup(name='dap.responses.wms',
      version=version,
      description="WMS response for pydap server",
      long_description="""\
pydap--WMS bridge.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/responses/wms#egg=dap.responses.wms-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='wms dap opendap dods data',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/responses/wms',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['dap.responses'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          #'PIL',
          'dap[server]>=2.2.5.1',
          'Paste',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [dap.response]
      wms = dap.responses.wms
      kml = dap.responses.wms.kml
      """,
      )
      
