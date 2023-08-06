#!/bin/env python

from distutils.core import setup

setup ( name="XRecord",
        description='An Introspecting Python ORM',
        version="0.1.2",
        url='http://xrecord.sourceforge.net/',
        author='Jakub Wroniecki',
        author_email='wroniasty@gmail.com',
        packages = ["XRecord"],
        package_dir = { 'XRecord' : 'src' },
        package_data = { 'XRecord' : ['samples/*'] }
        )
