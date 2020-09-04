#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'mitama',
    version = '1.0.0',
    install_requires = ['sqlalchemy', 'aiohttp', 'bcrypt', 'aiohttp_session', 'pyjwt', 'jinja2', 'cryptography'],
    extra_requires = {
        'develop': ['pytest']
    },
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'mitama = mitama.command:exec'
        ]
    }
)
