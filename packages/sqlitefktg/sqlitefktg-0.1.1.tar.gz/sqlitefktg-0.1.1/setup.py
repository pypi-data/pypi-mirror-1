#!/bin/env python

from distutils.core import setup
from src.sqlitefktg import version

setup ( name="sqlitefktg",
        description='SQLite foreign key trigger generator',
        version=version,
        url='http://coobs.eu.org/sqlitefktg/',
        author='Jakub Wroniecki',
        author_email='wroniasty@gmail.com',
        packages = ["sqlitefktg"],
        package_dir = { '' : 'src'},        
        scripts=['src/sqlitefk'],
        license = "BSD",
        classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: SQL',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',                                    
        ],
        download_url = 'https://coobs.eu.org/sqlitefktg/download.php',
        long_description = """
SQLite parses and stores foreign key constraints, but does not enforce them. The
simple solution of this problem is creating insert,update and delete triggers which
mimic the enforcing behaviour of other RDBMS. sqlitefktg does just that - automatically.

Features
========

  * automatic generation of foreign key enforcing triggers based on the data fetched from the database,
  * may be used as a command-line tool, as well as inside your own application,
  * 2-phase detection/generation process allows the advanced user to customize the end result.

`More information here <http://coobs.eu.org/sqlitefktg/>`_
"""
        )
