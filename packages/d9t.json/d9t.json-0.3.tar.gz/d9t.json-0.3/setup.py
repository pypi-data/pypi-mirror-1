from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='d9t.json',
      version=version,
      description="A json parser",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("d9t", "json", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='json d9t',
      author='D9T GmbH, Daniel Kraft',
      author_email='dk@d9t.de',
      url='http://d9t.de/os',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup', 'tests']),
      namespace_packages=['d9t'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      test_suite="d9t.json.tests.suite",
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
