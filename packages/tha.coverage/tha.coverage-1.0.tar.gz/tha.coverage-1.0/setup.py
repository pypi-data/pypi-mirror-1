from setuptools import setup, find_packages
import os.path

version = '1.0'

readme = open('README.txt').read()
changes = open('CHANGES.txt').read()
todo = open('TODO.txt').read()
usage = open(os.path.join('src', 'tha',
                             'coverage', 'USAGE.txt')).read()

long_description = '\n\n'.join([readme, todo, changes, ''])
# ^^^ USAGE.txt is omitted here.  Waaaay too much weird testing which is not
# useful for the user of this library.

setup(name='tha.coverage',
      version=version,
      description="Provides single script to create coverage reports",
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[],
      keywords=[],
      author='The Health Agency',
      author_email='techniek@thehealthagency.com',
      url='http://www.thehealthagency.com',
      license='BSD',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      namespace_packages=['tha'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'z3c.coverage',
                        # Add extra requirements here
                        ],
      extras_require = {
          'test': ['z3c.testsetup>=0.3'],
          },
      entry_points={
          'console_scripts': [
              'createcoverage = tha.coverage.script:main',
          ]},
      )
