from setuptools import setup, find_packages
import sys, os

from restez.version import version

setup(
    name='restez',
    version=version,
    description="A RESTful HTTP command-line client and library.",
    long_description="""\
    """,
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='REST RESTful HTTP client CLI shell python',
    author='Chris Miles',
    author_email='miles.chris@gmail.com',
    url='http://code.google.com/p/restez/',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
      # -*- Extra requirements: -*-
    ],
    entry_points = {
      'console_scripts': [
          'restez = restez.restez:main',
      ],
    },
)
