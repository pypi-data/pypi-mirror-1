from setuptools import setup, find_packages
import os

version = '1.0'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Detailed Documentation\n'
        '**********************\n'
        + '\n' +
        read('bliptv', 'reader', 'README.txt')
        + '\n' +
        'Download\n'
        '**********************\n'
        )


setup(name='bliptv.reader',
      version=version,
      description="A library for reading video episodes from any blip.tv show",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='bliptv video socialnetworking socialmedia newmedia library screenscraping blip',
      author='Christian Scholz',
      author_email='mrtopf@gmail.com',
      url='http://comlounge.net',
      license='LGPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['bliptv'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'elementtree'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
