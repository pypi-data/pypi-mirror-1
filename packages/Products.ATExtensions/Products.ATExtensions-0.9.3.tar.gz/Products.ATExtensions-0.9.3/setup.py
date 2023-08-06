from setuptools import setup, find_packages
import os

version = '0.9.3'

setup(name='Products.ATExtensions',
      version=version,
      description="This package provides some further fields and widgets for archetypes.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Raphael Ritz',
      author_email='r.ritz@biologie.hu-berlin.de',
      url='http://svn.plone.org/svn/archetypes/Products.ATExtensions',
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
