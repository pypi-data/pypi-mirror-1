from setuptools import setup, find_packages
import os

version = '0.5.0'

setup(name='Products.PortalTaxonomy',
      version=version,
      description="Provides a way to create a treeish category structure and then limit the association of content instances to specific sections of the tree.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Plone, Taxonomy',
      author='Jeremy Stark',
      author_email='jeremy@deximer.com',
      url='http://plone.org/products/portal_taxonomy',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
