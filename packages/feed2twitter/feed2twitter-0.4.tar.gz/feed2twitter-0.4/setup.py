from setuptools import setup, find_packages
from pkg_resources import resource_string
VERSION = resource_string(__name__, 'VERSION').strip()

setup(name='feed2twitter',
      version=VERSION,
      py_modules=['feed2twitter'],
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
      zip_safe=False,
      scripts=['scripts/feed2twitter'],
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
