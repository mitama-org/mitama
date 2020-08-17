#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'mitama',
    version = '1.0.0',
    install_requires = ['sqlalchemy', 'aiohttp'],
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'mitama = mitama.command:exec'
        ]
    }
)
