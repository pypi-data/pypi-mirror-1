
from setuptools import setup, find_packages
import sys, os

version = '0.9.1'

try:
    f = open(os.path.join(os.path.dirname(__file__), 'docs', 'index.txt'))
    long_description = f.read().strip()
    f.close()
except IOError:
    long_description = None

setup(name='sqlturk',
      version=version,
      description="Database schema migration tool",
      long_description=long_description,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Topic :: Software Development',
      ],
      keywords='sql database schema migration evolution migrate sqlalchemy',
      author='Max Ischenko',
      author_email='ischenko@gmail.com',
      url='http://bitbucket.org/max/sqlturk/',
      license='Apache License, Version 2.0',
      packages=find_packages(exclude=[]),
      include_package_data=True,
      test_suite = "nose.collector",
      zip_safe=True,
      install_requires=[
          "SQLAlchemy",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
