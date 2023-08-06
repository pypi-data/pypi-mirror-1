from setuptools import setup, find_packages
import os

version = '1.3.2'

setup(name='plonetheme.portaltwodotoh',
      version=version,
      description="An elastic lounded corners.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='Daniel Kvaternik',
      author_email='dkvaternik@nngov.com',
      url='http://svn.plone.org/svn/collective/plonetheme.portaltwodotoh/',
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
