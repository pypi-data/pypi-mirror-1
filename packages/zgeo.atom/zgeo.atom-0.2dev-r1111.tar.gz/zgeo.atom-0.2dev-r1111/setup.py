from setuptools import setup, find_packages

version = '0.2'

setup(name='zgeo.atom',
      version=version,
      description="Atom syndication with GeoRSS",
      long_description="""Provides Atom entry, subscription feed, and search feed documents annotated with GeoRSS elements.
      
Version 0.2 is incompatible with version 0.1
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
      keywords='gis geography geospatial georss atom',
      author='Sean Gillies',
      author_email='sgillies@frii.com',
      url='http://trac.gispython.org/projects/PrimaGIS/wiki/zgeo.atom',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zgeo'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
        'zgeo.geographer>=0.2dev',
      ],
      extras_require = {
        'bbox search': ['zgeo.spatialindex>=0.2dev'],
        },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
