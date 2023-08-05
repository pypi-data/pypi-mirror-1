from setuptools import setup, find_packages

version = '0.3'

setup(name='zgeo.spatialindex',
      version=version,
      description="Spatial index for Zope",
      long_description="""A R-Tree spatial index for geographically annotated objects that plugs into the Zope catalog and enables fast spatial bounding box searches.
      
Version 0.3 is incompatible with version 0.2.

Changes
=======

0.3: 18 February 2008
---------------------
- Implements an Rtree-based index that plugs into the Zope catalog.
- ISpatialIndex adapter has been removed.
""",
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
      keywords='gis geo spatial index',
      author='Sean Gillies',
      author_email='sgillies@frii.com',
      url='http://trac.gispython.org/projects/PrimaGIS/wiki/zgeo.spatialindex',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zgeo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Rtree',
          'Shapely',
          'zope.app.catalog',
          'zgeo.geographer>=0.3',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
