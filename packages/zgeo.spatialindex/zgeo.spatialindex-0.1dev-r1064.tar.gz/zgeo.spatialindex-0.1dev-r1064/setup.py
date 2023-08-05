from setuptools import setup, find_packages

version = '0.1'

setup(name='zgeo.spatialindex',
      version=version,
      description="Spatial index for Zope",
      long_description="A container-local R-Tree spatial index for geographically annotated objects, enabling fast spatial bounding box searches.",
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
      url='http://trac.gispython.org/projects/PrimaGIS/wiki',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zgeo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Rtree',
          'Shapely',
          'zgeo.geographer',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
