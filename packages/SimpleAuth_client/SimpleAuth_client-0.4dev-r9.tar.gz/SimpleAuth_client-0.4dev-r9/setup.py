import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

import sys, os

version = '0.4'

setup(name='SimpleAuth_client',
      version=version,
      description="client for the SimpleAuth application",
      long_description="""\
      A client for the SimpleAuth application that allows python access to SimpleAuth
      without requiring a full server install where the application is intended to be used.
      Simplifies it's integration as a plugin to other systems without expecting a full install.
""",
      classifiers=[], 
      keywords='simpleauth',
      author='James Taylor',
      author_email='baldtrol@gmail.com',
      url='http://www.simpleauth.com',
      download_url='http://simpleauth.googlecode.com/svn/projects/simpleauth_client/trunk',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          "SQLAlchemy >= 0.3", 
      ],
      entry_points="""

      """,
      )
      
