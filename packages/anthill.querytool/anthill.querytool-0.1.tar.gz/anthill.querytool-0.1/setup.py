from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='anthill.querytool',
      version=version,
      description="GUI for AdvancedQuery with some extensions - searching the easy way for Plone",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='anthill plone query advancedquery search',
      author='Simon Pamies',
      author_email='s.pamies@banality.de',
      url='http://www.banality.de/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['anthill'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
