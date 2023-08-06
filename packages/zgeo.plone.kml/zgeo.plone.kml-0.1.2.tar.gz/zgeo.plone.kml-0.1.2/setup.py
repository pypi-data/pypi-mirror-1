from setuptools import setup, find_packages

version = '0.1.2'

setup(name='zgeo.plone.kml',
      version=version,
      description="KML for Plone content",
      long_description="Provides KML views of georeferenced objects, allowing Plone containers and collections to be visualized in Google Earth.",
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: GIS",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        ],
      keywords='plone geo gis kml google earth',
      author='Sean Gillies',
      author_email='sgillies@frii.com',
      url='http://trac.gispython.org/projects/PrimaGIS/wiki/zgeo.plone.kml',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zgeo', 'zgeo.plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zgeo.kml>=0.3'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
