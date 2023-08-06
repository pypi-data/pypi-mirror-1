from setuptools import setup, find_packages
import os

version = '1.0b1'

setup(name='collective.portlet.accuweather',
      version=version,
      description="Weather portlet",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='plone weather portlet',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://pypi.python.org/pypi/collective.portlet.accuweather',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.portlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'FeedParser',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
