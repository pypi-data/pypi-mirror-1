from setuptools import setup, find_packages
import os

version = '1.2'

setup(name='Products.PageCacheManager',
      version=version,
      description="Cache rendered pages including headers",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='caching zope CMF',
      author='Geoff Davis',
      author_email='geoff@geoffdavis.net',
      url='http://svn.plone.org/svn/collective/Products.PageCacheManager',
      license='ZPL',
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
