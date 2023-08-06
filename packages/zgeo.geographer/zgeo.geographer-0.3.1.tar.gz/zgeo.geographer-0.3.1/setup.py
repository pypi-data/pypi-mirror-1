from setuptools import setup, find_packages
import sys, os

version = '0.3.1'

changes_txt = open('CHANGES.txt').read()

setup(name='zgeo.geographer',
      version=version,
      description="Geographic annotation for Zope",
      long_description="""Describes an interfaces for annotating objects with geographic location metadata and provides a standard annotator.
      
 Version 0.3 is not compatible with 0.2.

""" + changes_txt,
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: GIS",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License"
        ],
      keywords='gis geography geospatial',
      author='Sean Gillies',
      author_email='sgillies@frii.com',
      url='http://trac.gispython.org/projects/PrimaGIS/wiki/zgeo.geographer',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zgeo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

