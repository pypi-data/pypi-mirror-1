#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Doug Fort on 2006-09-28.
Copyright (c) 2006 Doug Fort Consultiing, Inc.. All rights reserved.
"""
from distutils.core import setup

setup(
    name="spasmoidal",
    version="0.1.1",
    description="Spasmodic Engine",
    url="http://code.google.com/p/spasmoidal/",
    maintainer="Doug Fort",
    maintainer_email="dougfort@dougfort.com",
    packages=['spasmoidal','spasmoidal.examples.echo'],
    package_dir = {'spasmoidal' : ''}
 )

