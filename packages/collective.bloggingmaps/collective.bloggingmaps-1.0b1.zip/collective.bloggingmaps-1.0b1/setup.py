from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='collective.bloggingmaps',
      version=version,
      description="An extension for Plone which adds google maps support for collective.blogging package.",
      long_description=open(os.path.join("collective", "bloggingmaps", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone blogging maps',
      author='Lukas Zdych',
      author_email='lukas.zdych@gmail.com',
      url='http://plone.org/products/collective.bloggingmaps',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.blogging',
          'Products.Maps',
          'archetypes.schemaextender',
          'archetypes.markerfield',
      ],
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins = ["ZopeSkel"],
      )
