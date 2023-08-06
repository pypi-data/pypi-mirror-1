from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='taras.python26',
      version=version,
      description="Collection of useful functions from python2.6 that can be used in python 2.5. Namely: subprocess",
      long_description="""\
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python2.6 subprocess',
      author='Taras Mankovski',
      author_email='tarasm@gmail.com',
      url='http://github.com/taras/taras.python26',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages = ['taras'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
