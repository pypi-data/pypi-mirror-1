# -*- coding: utf-8 -*-
# 
#  setup.py
#  from-camel
#  
#  Created by Lars Yencken on 2009-04-09.
#  Copyright 2009 Lars Yencken. All rights reserved.
# 

from setuptools import setup

VERSION = '0.2.0'

setup(
        name='from-camel',
        description="A script to convert python files from camel case variable naming to underscore variable naming.",
        long_description = """
        Provides a convenience script for changing varaible and method naming
        in your python files from camel case to underscore notation. For
        example, oneMoreVariable would be renamed to one_more_variable. Backs
        up all your original files so you can easily revert.
        """,
        url="http://bitbucket.org/lars512/from-camel/",
        version=VERSION,
        author="Lars Yencken",
        author_email="lljy@csse.unimelb.edu.au",
        license="BSD",
        install_requires=[],
        packages=[],
        scripts=['from_camel'],
    )
