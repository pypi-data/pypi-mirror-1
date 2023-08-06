#!/usr/bin/env python

from setuptools import setup, find_packages


setup(name='pgmigrate',
      version='1.1',
      description='Database schema migration tool for Postgres',
      author='Sergey Kirillov',
      author_email='sergey.kirillov@gmail.com',
      url='http://code.google.com/p/pgmigrate/',
      packages=find_packages(),
      scripts=['pgmigrate.py'],
      install_requires=['lxml'],
      license="Apache License 2.0",
      keywords="database migration tool postgres",
      zip_safe=True,

    entry_points = {
        'console_scripts': [
            'pgmigrate = pgmigrate:main',
        ],
    }	
)

