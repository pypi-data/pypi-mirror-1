from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='collective.jqganalytics',
      version=version,
      description="A jQuery based load and set of Google Analytics",
      long_description=open(os.path.join("docs", "README")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone analytics',
      author='Texas A&M University Library',
      author_email='webmaster@library.tamu.edu',
      maintainer='Benjamin Liles',
      maintainer_email='bliles@library.tamu.edu',
      url='http://plone.org/products/collective.jqganalytics/',
      license='ZPL',
      packages=find_packages(),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],)
