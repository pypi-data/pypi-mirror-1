from setuptools import setup, find_packages

version = '0.2'

setup(name='zgeo.plone.atom',
      version=version,
      description="Plone specific Atom syndication with GeoRSS",
      long_description="""\
""",
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
      keywords='plone geo gis georss atom',
      author='Sean Gillies',
      author_email='sgillies@frii.com',
      url='http://trac.gispython.org/projects/PrimaGIS/wiki/zgeo.plone.atom',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zgeo', 'zgeo.plone'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'zgeo.atom>=0.4'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
