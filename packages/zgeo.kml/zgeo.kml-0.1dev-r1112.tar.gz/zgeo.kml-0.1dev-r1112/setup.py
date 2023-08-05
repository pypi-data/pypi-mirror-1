from setuptools import setup, find_packages

version = '0.1'

setup(name='zgeo.kml',
      version=version,
      description="Google Earth KML for Zope",
      long_description="Provides KML views of georeferenced objects, allowing Zope containers to be visualized in Google Earth.",
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
      keywords='gis geography geospatial kml google earth',
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
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
