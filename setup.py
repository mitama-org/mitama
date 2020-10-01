#!/usr/bin/python

from setuptools import setup

setup(
    name = 'mitama',
    version = '1.0.1',
    install_requires = ['sqlalchemy', 'aiohttp', 'bcrypt', 'pyjwt', 'jinja2', 'cryptography', 'python-magic'],
    extra_requires = {
        'develop': ['pytest']
    },
    packages = ['mitama'],
    package_dir = {'mitama': 'mitama'},
    package_data = {
        'mitama': [
            'portal/templates/*.html',
            'portal/templates/**/*.html',
            'portal/static/*',
            'skeleton/templates/*.html',
            'skeleton/static/*',
            'http/templates/*.html',
            'app/static/*',
        ]
    },
    entry_points = {
        'console_scripts': [
            'mitama = mitama.command:exec'
        ]
    }
)
