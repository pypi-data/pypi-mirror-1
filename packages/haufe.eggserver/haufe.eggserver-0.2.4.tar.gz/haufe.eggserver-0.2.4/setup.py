import os
from setuptools import setup, find_packages

version = '0.2.4'
long_desc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()
changes = open(os.path.join(os.path.dirname(__file__), 'CHANGES.txt')).read()
long_desc += '\nCHANGES\n=======\n\n' + changes

setup(name='haufe.eggserver',
      version=version,
      description="A small PyPI replacement based on a local distribution directory (implemented using GROK)",
      long_description=long_desc,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[], 
      keywords="",
      author="Andreas Jung",
      author_email="info@zopyx.com",
      url="",
      license="ZPL 2.1",
      package_dir={'': 'src'},
      packages=find_packages('src'),
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'grok',
                        'gocept.cache',
                        # Add extra requirements here
                        ],
      entry_points="""
      # Add entry points here
      """,
      )
