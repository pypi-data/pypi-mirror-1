from setuptools import setup, find_packages

version = '0.1'

setup(name='zgeo.plone.geographer',
      version=version,
      description="Geographic annotation for Plone",
      long_description="""\
""",
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
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
      keywords='gis geography geospatial plone',
      author='Sean Gillies',
      author_email='sgillies@frii.com',
      url='http://trac.gispython.org/projects/PrimaGIS/wiki/zgeo.plone.geographer',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zgeo', 'zgeo.plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zgeo.geographer>=0.3'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
