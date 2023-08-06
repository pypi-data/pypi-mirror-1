from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "CacheSetup", "VERSION.txt")).read().strip()

setup(name='Products.CacheSetup',
      version=version,
      description="Control caching of Plone sites",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n" +
                       open(os.path.join("docs", "CHANGES.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='cache caching',
      author='Geoff Davis',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://svn.plone.org/svn/collective/Products.CacheSetup',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFSquidTool',
          'Products.PageCacheManager',
          'Products.PolicyHTTPCacheManager',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
