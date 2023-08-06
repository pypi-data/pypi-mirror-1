from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='five.caching',
      version=version,
      description="Zope2 integration for z3c.caching",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Wichert Akkerman',
      author_email='wichert@wiggy.net',
      url='http://pypi.python.org/pypi/five.caching',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['five'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "Products.Archetypes",
          "Products.CMFCore",
          "Products.CacheSetup",
          "plone.postpublicationhook",
          "setuptools",
          "z3c.caching",
          "zope.component",
          "zope.dublincore",
          "zope.interface",
          "zope.publisher",
      ],
      )
