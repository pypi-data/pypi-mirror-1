from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='vs.event',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='Zope Plone Event Recurrence',
      author='Veit Schiele, Anne Walther, Andreas Jung',
      author_email='idg@veit-schiele.de',
#      url='http://172.25.16.211/svn/plone/vs.event',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['vs'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'dateable.chronos',
          'dateable.kalends',
          'p4a.ploneevent',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
