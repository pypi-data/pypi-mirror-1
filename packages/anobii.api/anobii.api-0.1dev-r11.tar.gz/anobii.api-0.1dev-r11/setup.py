from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='anobii.api',
      version=version,
      description="wrapper for Anobii API",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='anobii api python',
      author='Massimo Azzolini',
      author_email='massimo.azzolini@gmail.com',
      url='http://code.google.com/p/anobiiapi/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['anobii'],
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
