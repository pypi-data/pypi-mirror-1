from setuptools import setup, find_packages
import os

version = '1.21'

setup(name='qi.portlet.TagClouds',
      version=version,
      description="A configurable plone portlet that displays tag clouds",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone tag cloud portlet',
      author='G. Gozadinos',
      author_email='ggozad@qiweb.net',
      url='http://qiweb.net',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['qi', 'qi.portlet'],
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
