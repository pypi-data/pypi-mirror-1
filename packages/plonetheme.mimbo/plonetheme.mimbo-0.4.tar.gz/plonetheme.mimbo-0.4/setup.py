from setuptools import setup, find_packages
import os

version_file = os.path.join('plonetheme', 'mimbo', 'version.txt')
version = open(version_file).read().strip()

setup(name='plonetheme.mimbo',
      version=version,
      description="An installable theme for Plone 3.0 based on the Mimbo theme by Darren Hoyt",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='Timo Stollenwerk',
      author_email='timo@zmag.de',
      url='http://svn.plone.org/svn/collective/plonetheme.mimbo',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plonetheme'],
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
