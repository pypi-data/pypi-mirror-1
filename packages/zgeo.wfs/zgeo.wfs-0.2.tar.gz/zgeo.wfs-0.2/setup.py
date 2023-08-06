from setuptools import setup, find_packages
import os

version = '0.2'

setup(name='zgeo.wfs',
      version=version,
      description="WFS server implementation for Zope",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='gis geography wfs',
      author='Eric BREHAULT',
      author_email='eric.brehault@makina-corpus.org',
      url='http://trac.gispython.org/primagis/wiki/zgeo.wfs',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zgeo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Shapely',
          'Rtree',
          'zgeo.geographer',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
