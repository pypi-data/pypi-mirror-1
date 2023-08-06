from setuptools import setup, find_packages
import sys, os

version_file = os.path.join('html2docbook', 'version.txt')
version = open(version_file).read().strip()

readme_file = os.path.join('html2docbook', 'README.txt')
desc = open(readme_file).read().strip()

changes_file = os.path.join('html2docbook', 'CHANGES.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nChanges:\n========\n\n' + changes

setup(name='html2docbook',
      version=version,
      description="HTML to DocBook transformation",
      long_description=long_description,
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='Timo Stollenwerk',
      author_email='timo@zmag.de',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      test_requires=['nose'],
      install_requires=[
          # -*- Extra requirements: -*-
          'nose',
          'BeautifulSoup',
          'lxml',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
