from setuptools import setup, find_packages
import os
import re

v = file(os.path.join(os.path.dirname(__file__), 'postcoder', '__init__.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

setup(name='PostCoder',
      version=VERSION,
      description="A simple API in python to work with \
      postcoder, a popular web service for addresses & \
      postcodes in the UK \
      ",
      long_description="""\

This module can be used with postcoder webservice to
get addresses from postcoder against post codes and 
vice versa. It implements the complete SOAP methods
implemented by postcoder.

It implements the following SOAP methods:
* getThrfareAddresses
* getPremiseList
* getMatchAddress
* getGrids
* getPostzon
and a helper function to calculate distance
between two postcodes

""",
      classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'Programming Language :: Python',
      ],
      keywords='postcoder UK postcodes',
      author='Sharoon Thomas',
      author_email='sharoon.thomas@openlabs.co.in',
      url='http://www.openlabs.co.in',
      license='MIT',
      packages=find_packages('.', exclude=['ez_setup', 'examples']),
      zip_safe=False,
      install_requires=[
          'suds>=0.3.8',
      ],
)
