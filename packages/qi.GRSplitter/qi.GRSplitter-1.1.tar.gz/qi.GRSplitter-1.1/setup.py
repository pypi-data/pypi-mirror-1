from setuptools import setup, find_packages
import os

version = '1.1'

setup(name='qi.GRSplitter',
      version=version,
      description="Greek word splitter for ZCTextIndex",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zope greek ZCTextIndex Splitter',
      author='G. Gozadinos',
      author_email='ggozad@qiweb.net',
      url='http://svn.plone.org/svn/collective/qi.GRSplitter',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['qi'],
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
