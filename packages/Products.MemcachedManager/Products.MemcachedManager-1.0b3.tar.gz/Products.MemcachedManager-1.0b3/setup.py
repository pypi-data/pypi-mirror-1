from setuptools import setup, find_packages
import os

version = '1.0b3'

setup(name='Products.MemcachedManager',
      version=version,
      description="Memcache cache manager for Zope",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Zope2",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='memcache Zope cache cachemanager',
      author='Sidnei da Silva',
      author_email='plone-developers@lists.sourceforge.net',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "setuptools",
          "python-memcached >= 1.40",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )

