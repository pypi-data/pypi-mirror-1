#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='ZOAuth',
    version='0.2',
    description="Zack's OAuth client library.",
    author='Zachary Voase',
    author_email='disturbyte@gmail.com',
    url='http://github.com/disturbyte/zoauth',
    packages=['zoauth', 'zoauth.support', 'zoauth.support.django']
)
