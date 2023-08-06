from setuptools import setup, find_packages
import sys, os

version = '1.4.3'

docs = [os.path.join('dupfinder','README.txt'),
        os.path.join('docs','HISTORY.txt')]

setup(name='dupfinder',
      version=version,
      description="Find and manage duplication files on the file system",
      long_description="\n\n".join([file(d).read() for d in docs]),
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='file duplication finder manager',
      author="Andriy Mylenkyy",
      author_email="mylanium@gmail.com",
      url="http://python.org/pypi/dupfinder",
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      namespace_packages = [],
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'console_scripts': [
              'dupfind = dupfinder.finder:main',
              'dupmanage = dupfinder.manager:main',
          ],
      },
      test_suite="dupfinder.tests.test_suite",
      tests_require=[],
      )
