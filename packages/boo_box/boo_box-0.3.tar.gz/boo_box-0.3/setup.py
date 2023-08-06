from setuptools import setup, find_packages
import sys, os

version = '0.3'

setup(name='boo_box',
      version=version,
      description="Boo-Box",
      long_description = open("README.txt").read(),
      classifiers=['Intended Audience :: Developers'
      'Development Status :: 4 - Beta'
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Programming Language :: Python'], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Walter Cruz',
      author_email='walter@waltercruz.com',
      url='http://www.assembla.com/spaces/py_boo_box',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
