#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'mitama',
    version = '1.0.2',
    install_requires = ['sqlalchemy', 'aiohttp', 'bcrypt', 'pyjwt', 'jinja2', 'cryptography', 'python-magic'],
    extra_requires = {
        'develop': ['pytest']
    },
    packages = find_packages(),
    package_data = {
        'mitama.portal': [
            'templates/*.html',
            'templates/**/*.html',
            'static/*',
        ],
        'mitama.skeleton': [
            'templates/*.html',
            'static/*',
        ],
        'mitama.http': [
            'templates/*.html',
        ],
        'mitama.app': [
            'static/*',
        ]
    },
    entry_points = {
        'console_scripts': [
            'mitama = mitama.command:exec'
        ]
    }
)
