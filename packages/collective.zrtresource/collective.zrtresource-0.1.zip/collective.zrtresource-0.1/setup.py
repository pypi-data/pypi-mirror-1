from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='collective.zrtresource',
      version=version,
      description="This package is a tiny wrapper around z3c.zrtresource so it works in Zope2 (tested with 2.10).",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone zrtresource',
      author='Tim Terlegard, JC Brand',
      author_email='jc@opkode.com',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'z3c.zrtresource',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
