#!/bin/env python

from distutils.core import setup

setup ( name="XRecord",
        description='An Introspecting Python ORM',
        version="0.1.5",
        url='http://xrecord.sourceforge.net/',
        author='Jakub Wroniecki',
        author_email='wroniasty@gmail.com',
        packages = ["XRecord"],
        package_dir = { 'XRecord' : 'src' },
        package_data = { 'XRecord' : ['samples/*'] },
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
        download_url = 'https://sourceforge.net/projects/xrecord/files/',
        long_description = """
XRecord is not an attempt to match the functionality of existing ORMs. 
It's designed as a plug and play component to a well defined, 
(foreign keys, primary keys, references) already existing database.

Features
========

  * full introspection, no model definition in Python required,
  * may store meta-data to improve performance in production environments,
  * automatic foreign key mapping, both in the referenced and referencing objects,
  * automatic many-to-many relationship detection,
  * optional foreign-key references caching,
  * easily extend generated record classes to provide extra functionality for your objects,
  * easily define FK and MTM relationships, that were left out in the database definition,
  * object-mapping of any SQL statement,
  * may be used without writing a single line of SQL,
  * multiple-column primary keys,
  * database connection objects designed for long-running applications

"""
        )
