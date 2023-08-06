from setuptools import setup, find_packages
import sys, os

version = '0.2'

setup(name='rstctl',
      version=version,
      description="reST utils",
      long_description=open('README.txt').read() + open('CHANGES.txt').read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          'Environment :: Console',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: OS Independent',
          'Topic :: Utilities',
          ],
      keywords='reST',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://www.gawel.org',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'docutils',
          'Sphinx',
          'Pygments',
          'PasteScript',
          'Mako',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      rstctl = rstctl:main
      """,
      )
