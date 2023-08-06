from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='tgext.crud',
      version=version,
      description="Crud Controller Extension for TG2",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='TG, TG2, REST, sprox',
      author='Christopher Perkins',
      author_email='chris@percious.com',
      url='',
      license='MIT',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['tgext'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'sprox',
          'tw.dojo',
          'tw.forms',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
