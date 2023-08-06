from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(name='redturtle.catalogmount',
      version=version,
      description="Small package which helps mount portal_catalog to separate ZODB.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone ZODB mount Catalog portal_catalog',
      author='Andrew Mleczko',
      author_email='andrew.mleczko@redturtle.net',
      url='http://www.redturtle.net',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['redturtle'],
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
