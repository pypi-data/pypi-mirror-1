from setuptools import setup, find_packages
import os

version = '2.1.1'

setup(name='Products.AutoRole',
      version=version,
      description="PAS plugin for adding roles to (anonymous or logged-in) "
                  "visitors based on their IP address.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='autorole pas plugin roles groups',
      author='Jarn',
      author_email='info@jarn.com',
      url='http://plone.org/products/autorole',
      license='LGPL',
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
