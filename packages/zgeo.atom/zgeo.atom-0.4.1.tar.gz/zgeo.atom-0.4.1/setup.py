from setuptools import setup, find_packages

version = '0.4.1'
readme_text = open('README.txt', 'rb').read()

setup(name='zgeo.atom',
      version=version,
      description="Atom syndication and AtomPub with GeoRSS",
      long_description=readme_text,
      classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: GIS",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License"
        ],
      keywords='gis geography geospatial georss atom atompub',
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
        'zgeo.geographer>=0.3',
      ],
      extras_require = {
        'bbox search': ['zgeo.spatialindex>=0.3'],
        },
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
