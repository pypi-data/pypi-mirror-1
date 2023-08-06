#!/usr/bin/python
try:
    import setuptools
except ImportError:

    import ez_setup
    ez_setup.use_setuptools()

from setuptools import setup, find_packages
import sys, os

setup(
    name='hgpasteapp',
    version='0.1.3',
    description='Simple wrapper to hgweb that has paster app_factory entrypoints.',
    author='Maries Ionel Cristian',
    author_email='ionel.mc@gmail.com',
    packages=['hgpasteapp'],
    zip_safe=True,
    classifiers=[
    ],
    entry_points={
        'paste.app_factory': [
            'hgweb=hgpasteapp:hgweb_app_factory',
            'hgwebdir=hgpasteapp:hgwebdir_app_factory',
        ],
	'console_scripts': []
    },
    console_scripts=[],
    install_requires = ["mercurial", "PasteDeploy"]
)
