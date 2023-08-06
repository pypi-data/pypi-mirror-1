from setuptools import setup, find_packages
from pkg_resources import resource_string
import os
import re
import sys

v = file(os.path.join(os.path.dirname(__file__), 'feed2twitter', '__init__.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)

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
      packages=['feed2twitter','docs'],
      #package_data = {'docs':['*']},
      include_package_data=True,
      license='AGPL',
      zip_safe=False,
      scripts=['scripts/feed2twitter'],
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
