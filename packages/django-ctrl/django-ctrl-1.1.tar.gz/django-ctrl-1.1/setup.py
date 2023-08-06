#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name='django-ctrl',
    version='1.1',
    description='An implementation of Controllers for Django.',
    author='Zachary Voase',
    author_email='zacharyvoase@me.com',
    url='http://bitbucket.org/zacharyvoase/django-ctrl/',
    packages=['djctrl', 'djctrl.http'],
)
