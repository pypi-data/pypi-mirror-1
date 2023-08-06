from setuptools import setup, find_packages
import os

version = '0.13.1'

setup(name='Products.XMLWidgets',
      version=version,
      description="XMLWidgets is a Zope 2 product used to create through the web viewers and editors of ParsedXML content.",
      long_description=open(os.path.join("Products", "XMLWidgets", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "XMLWidgets", "CREDITS.txt")).read() + "\n" +
                       open(os.path.join("Products", "XMLWidgets", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: BSD License",
              "Programming Language :: Python",
              "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
              "Topic :: Software Development :: Libraries :: Python Modules",
              "Topic :: Software Development :: Widget Sets",
              "Topic :: Text Processing :: Markup :: HTML",
              "Topic :: Text Processing :: Markup :: XML",
              ],
      keywords='xml rendering zope2 parsedxml',
      author='Martijn Faassen',
      author_email='info@infrae.com',
      url='http://infrae.com/products/silva',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
              'setuptools',
              'Products.ParsedXML'
              ],
      )
