from setuptools import setup, find_packages
import os

version = '0.2.1'

setup(name='redturtle.maps.core',
      version=version,
      description="Every plone contents can be drawn on a Maps'map",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
	    "Framework :: Plone",
        ],
      keywords='maps contents plone',
      author='Andrew Mleczko, Massimo Azzolini, Luca Fabbri',
      author_email='massimo@redturtle.net',
      url='http://plone.org/products/redturtle-maps.core',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle', 'redturtle.maps'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.Maps',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
