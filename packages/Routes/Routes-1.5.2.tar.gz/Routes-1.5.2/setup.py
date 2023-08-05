from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name="Routes",
      version='1.5.2',
      description='Routing Recognition and Generation Tools',
      long_description="""
A Routing package for Python that matches URL's to dicts and vice versa

`Dev version available <http://routes.groovie.org/svn/trunk#egg=Routes-dev>`_
""",
      classifiers=["Development Status :: 5 - Production/Stable",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Programming Language :: Python",
                   "Topic :: Internet :: WWW/HTTP",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      author='Ben Bangert',
      author_email='ben@groovie.org',
      url='http://routes.groovie.org/',
      test_suite = 'nose.collector',
      packages=find_packages(exclude=['tests', 'ez_setup']),
      )
