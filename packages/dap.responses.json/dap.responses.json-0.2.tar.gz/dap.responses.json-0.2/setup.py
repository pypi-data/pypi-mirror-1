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

version = '0.2'

setup(name='dap.responses.json',
      version=version,
      description="JSON response for pydap server",
      long_description="""\
JSON representation of DAP datasets.

The latest version is available in a `Subversion repository
<http://pydap.googlecode.com/svn/trunk/responses/json#egg=dap.responses.json-dev>`_.""",
      classifiers=filter(None, classifiers.split("\n")),
      keywords='json dap opendap dods data',
      author='Roberto De Almeida',
      author_email='rob@pydap.org',
      url='http://pydap.org/responses/json',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['dap.responses'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'dap[server]>=2.2.4',
          'simplejson',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [dap.response]
      json = dap.responses.json
      """,
      )
      
