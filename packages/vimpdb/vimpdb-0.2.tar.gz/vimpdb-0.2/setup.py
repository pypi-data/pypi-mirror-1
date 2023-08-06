from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='vimpdb',
      version=version,
      description="VIM PDB support",
      long_description=file("vimpdb/README.txt").read(),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='vim pdb',
      author='Stefan Eletzhofer',
      author_email='stefan.eletzhofer@inquant.de',
      url='https://svn.plone.org/svn/collective/vimpdb/trunk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
