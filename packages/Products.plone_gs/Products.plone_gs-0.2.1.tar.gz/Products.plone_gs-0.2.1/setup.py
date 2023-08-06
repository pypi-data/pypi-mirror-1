__version__ = '0.2.1'

import os

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name='Products.plone_gs',
      version=__version__,
      description='GenericSetup support for Plone',
      long_description='\n\n'.join((README, CHANGES)),
      author="Tres Seaver, Agendaless Consulting",
      author_email="tseaver@agendaless.com",
      url="http://agendaless.com/software/plone_gs",
      license="ZPL",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      tests_require = [],
      install_requires=[],
      setup_requires=['setuptools'],
      entry_points = """\
      """
      )

