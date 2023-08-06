from setuptools import setup, find_packages
import sys, os

version = '0.3.7'

setup(name='boo_box',
      version=version,
      description="Boo-Box to monetize",
      long_description = open('README').read(),
      classifiers=['Intended Audience :: Developers',
      'Development Status :: 4 - Beta',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Programming Language :: Python'],
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
