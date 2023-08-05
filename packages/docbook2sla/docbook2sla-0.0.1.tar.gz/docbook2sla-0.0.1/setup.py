from setuptools import setup, find_packages
import sys, os

version = '0.0.1'

setup(name='docbook2sla',
      version=version,
      description="",
      long_description="""\
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
