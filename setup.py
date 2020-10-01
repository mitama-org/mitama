#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'mitama',
    version = '1.0.1',
    install_requires = ['sqlalchemy', 'aiohttp', 'bcrypt', 'pyjwt', 'jinja2', 'cryptography', 'python-magic'],
    extra_requires = {
        'develop': ['pytest']
    },
    packages = find_packages(),
    include_package_data = True,
    entry_points = {
        'console_scripts': [
            'mitama = mitama.command:exec'
        ]
    }
)
