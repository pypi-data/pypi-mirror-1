from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='Products.TemplateCacheManager',
      version=version,
      description="Cache rendered pages including headers with ETag support",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='caching zope CMF',
      author='Andreas Gabriel',
      author_email='gabriel@hrz.uni-marbug.de',
      url='http://svn.plone.org/svn/collective/Products.TemplateCacheManager',
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
