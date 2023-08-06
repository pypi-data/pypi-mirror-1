from setuptools import setup, find_packages
import os

version = '0.3'

setup(name='google.directions',
      version=version,
      description="A python api to google directions",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("google", "directions", "README.txt")).read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='google directions d9t',
      author='D9T GmbH, Daniel Kraft',
      author_email='dk@d9t.de',
      url='http://d9t.de/os',
      license='GPLv3',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['google'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'd9t.json',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
