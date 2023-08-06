from setuptools import setup, find_packages
import sys, os
from os import path
v = open(path.join(path.dirname(__file__), 'VERSION'))
VERSION = v.readline().strip()

setup(name='feed2twitter',
      version=VERSION,
      description="Publish your feed items to twitter",
      long_description=open('README').read(),
      classifiers=[
      "Intended Audience :: Developers",
      "Programming Language :: Python",
      "Environment :: Console",
      "Development Status :: 3 - Alpha"
      ],
      keywords='twitter feed',
      author='Walter Cruz',
      author_email='walter@waltercruz.com',
      url='http://www.assembla.com/spaces/feed2twitter',
      license='AGPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      scripts=['scripts/feed2twitter'],
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
