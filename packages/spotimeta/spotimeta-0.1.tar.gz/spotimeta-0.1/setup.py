from setuptools import setup, find_packages
import sys, os


import spotimeta # should be ok. No dependencies so import should never fail
author, email = spotimeta.__author__[:-1].split(' <')


setup(name='spotimeta',
      version=spotimeta.__version__,
      description=spotimeta.__doc__,
      long_description=open("README").read(),
      classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Spotify',
      author=author,
      author_email=email,
      url=spotimeta.__homepage__,
      license='BSD',
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
