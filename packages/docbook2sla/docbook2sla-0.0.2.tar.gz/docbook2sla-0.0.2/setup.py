from setuptools import setup, find_packages
import sys, os

version = '0.0.2'

setup(name='docbook2sla',
      version=version,
      description="A Python interface to convert DocBook to Scribus",
      long_description="""\The docbook2sla package helps you to convert DocBook XML into the Scribus
(http://www.scribus.net) file format.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='docbook scribus converter dtp',
      author='Timo Stollenwerk',
      author_email='timo@zmag.de',
      url='http://scribus.zmag.de',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'lxml',
          'zope.interface',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
