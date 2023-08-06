from setuptools import setup, find_packages
import os

version = '1.1b1'

setup(name='Products.sampleremember',
      version=version,
      description="Sample remember based custom member implementation",
      long_description=open(
          os.path.join("Products", "sampleremember",
                       "README.txt")).read() + "\n" + open(
          os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Rob Miller',
      author_email='robm@openplans.org',
      url='http://plone.org/products/products-remember',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'Products.remember',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
