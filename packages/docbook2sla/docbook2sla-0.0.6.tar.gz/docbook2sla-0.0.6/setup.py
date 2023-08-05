from setuptools import setup, find_packages
import sys, os

CLASSIFIERS = [
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Programming Language :: Python',
    'Development Status :: 2 - Pre-Alpha',
    'Intended Audience :: Developers',
    'Topic :: Internet',
    'Topic :: Multimedia :: Graphics :: Editors',
               ] # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers

version_file = os.path.join('docbook2sla', 'version.txt')
version = open(version_file).read().strip()

readme_file = os.path.join('docbook2sla', 'README.txt')
desc = open(readme_file).read().strip()

changes_file = os.path.join('docbook2sla', 'CHANGES.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nChanges:\n========\n\n' + changes

setup(name='docbook2sla',
      version=version,
      description="A Python interface to convert DocBook to Scribus",
      long_description=long_description,
      classifiers=CLASSIFIERS,
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
