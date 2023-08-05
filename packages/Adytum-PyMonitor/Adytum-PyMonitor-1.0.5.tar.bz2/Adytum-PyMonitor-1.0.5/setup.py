#!/usr/bin/env python

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup

version = open('VERSION').read().strip()

setup(name="Adytum-PyMonitor",
    version=version,
    description="Supporting python modules for the pymon monitoring tool",
    long_description="Supporting python modules for the pymon monitoring tool",
    author="Duncan McGreggor",
    author_email="duncan@adytum.us",
    url="http://projects.adytum.us/tracs/PyMonitor",
    download_url="http://projects.adytum.us/tracs/adytum/browser/releases/",
    namespace_packages = ['adytum'],
    packages=[
        'adytum',
        'adytum.config',
        'adytum.net',
        'adytum.os',
        'adytum.util',
        'adytum.workflow',
    ],
    package_dir = {'adytum': 'lib'},
)
