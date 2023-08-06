from setuptools import setup, find_packages
import os

version = '0.2.9'

setup(name='vs.event',
      version=version,
      description="An extended event content-type for Plone (and Plone4Artists calendar)",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Zope Plone Event Recurrence Calendar Plone4Artists',
      author='Veit Schiele, Anne Walther, Andreas Jung',
      author_email='vs.event@veit-schiele.de',
      url='http://svn.plone.org/svn/collective/vs.event',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vs'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'dateable.chronos',
          'dateable.kalends',
          'Products.DataGridField',
          'p4a.common',
          'p4a.ploneevent',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
