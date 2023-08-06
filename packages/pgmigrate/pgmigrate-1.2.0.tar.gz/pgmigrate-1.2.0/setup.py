#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='pgmigrate',
      
    packages=find_packages(),
    version='1.2.0',
    description='Database schema migration tool for Postgres',
    author='Sergey Kirillov',
    author_email='sergey.kirillov@gmail.com',
    url='http://code.google.com/p/pgmigrate/',
    install_requires=['lxml', 'psycopg2'],
    license="Apache License 2.0",
    keywords="database migration tool postgres",
    platforms = ["any"],
    classifiers = ["Programming Language :: Python",
#                       "License :: OSI Approved :: BSD License",
 #                      "Topic :: Software Development :: Libraries :: Python Modules",
                       "Operating System :: OS Independent",
                       "Natural Language :: English",
                   ],


    zip_safe=True,
      
    entry_points = {
        'console_scripts': [
            'pgmigrate = pgmigrate:main',
        ],
    }	
)

