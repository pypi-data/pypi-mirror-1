from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='pam',
      version=version,
      description="PAM interface using ctypes",
      long_description="""\
An interface to the Pluggable Authenticate Mechanism (PAM) library on linux, written in pure python (using ctypes)""",
      classifiers=["Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: System :: Systems Administration :: Authentication/Directory"
          ],
      keywords='',
      author='Chris AtLee',
      author_email='chris@atlee.ca',
      url='http://atlee.ca/software/pam',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
