from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='inqbus.plone.panorama',
      version=version,
      description="A Panorama Add-on for Plone, based on jquery and jquery.panorama.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Maik Derstappen - Derstappen IT Consulting',
      author_email='maik.derstappen@inqbus.de',
      url='http://www.inqbus-hosting.de/open-source-software/inqbus.plone.panorama',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['inqbus', 'inqbus.plone'],
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
