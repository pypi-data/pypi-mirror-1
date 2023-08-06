from setuptools import setup, find_packages
import os

version = '1.3'
name = 'collective.namedfile'

here=os.path.dirname(__file__)

longdesc = open(os.path.join(here, 'README.txt')).read() + '\n' + \
           open(os.path.join(here, 'docs', 'CHANGES.txt')).read()

setup(name='collective.namedfile',
      version=version,
      description="File field and widget with enhancements for zope3.",
      long_description=longdesc,
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
      author_email='l@lrowe.co.uk',
      maintainer='Laurence Rowe',
      maintainer_email='l@lrowe.co.uk',
      url='http://pypi.python.org/pypi/collective.namedfile',
      license='ZPL 2.1',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      )
