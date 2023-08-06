from setuptools import setup, find_packages
import os

version = '1.5'

setup(name='Products.ParsedXML',
      version=version,
      description="Parsed XML allows you to use XML objects in the Zope 2 environment.",
      long_description=open(os.path.join("Products", "ParsedXML", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "ParsedXML", "CREDITS.txt")).read() + "\n" +
                       open(os.path.join("Products", "ParsedXML", "CHANGES.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
              "Framework :: Zope2",
              "License :: OSI Approved :: Zope Public License",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              "Topic :: Text Processing :: Markup :: XML",
              ],
      keywords='parsedxml xml zope2',
      author='Zope community, and various others contributors',
      author_email='info@infrae.com',
      url='http://www.zope.org/Members/faassen/ParsedXML',
      license='ZPL 2.0 and Fourthought license',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
              'setuptools',
              ],
      )
