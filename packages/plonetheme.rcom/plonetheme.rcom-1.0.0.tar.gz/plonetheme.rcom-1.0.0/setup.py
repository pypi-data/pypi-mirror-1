import os
from setuptools import setup, find_packages

version_file = os.path.join('plonetheme', 'rcom', 'version.txt')
version = open(version_file).read().strip()

setup(name='plonetheme.rcom',
      version=version,
      description="An installable theme for Plone 3.0.",
      long_description=open("README.txt").read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='web zope plone theme',
      author='Roman Mottino',
      author_email='roman.mottino@rcom.com.ar',
      url='http://www.rcom.com.ar/',
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
