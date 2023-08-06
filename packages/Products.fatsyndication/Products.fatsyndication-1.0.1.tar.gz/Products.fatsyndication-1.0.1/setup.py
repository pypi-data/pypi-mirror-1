from setuptools import setup, find_packages
import os

version = '1.0.1'

setup(name='Products.fatsyndication',
      version=version,
      description="Archetypes implementation for basesyndication",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='syndication atom rss plone',
      author='Tim Hicks',
      author_email='tim@sitefusion.co.uk',
      url='http://dev.plone.org/collective/browser/Products.fatsyndication',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.basesyndication'
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
