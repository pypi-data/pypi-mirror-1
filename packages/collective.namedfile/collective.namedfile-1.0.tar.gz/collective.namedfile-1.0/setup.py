from setuptools import setup, find_packages
import os

version = '1.0'
name = 'collective.namedfile'

longdesc = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='collective.namedfile',
      version=version,
      description="File field and widget with enhancements for zope3.",
      long_description=longdesc,
      # Get more strings from http://www.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Framework :: Zope3",
        "Programming Language :: Python",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
      keywords='',
      author='Wichert Akkerman, Martijn Pieters, Laurence Rowe',
      author_email='',
      maintainer='Laurence Rowe',
      maintainer_email='l@lrowe.co.uk',
      url='http://svn.plone.org/svn/collective/collective.namedfile',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # no zope dependencies here 
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
