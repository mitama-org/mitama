#!/usr/bin/python

from setuptools import setup, find_packages

setup(
    name = 'mitama',
    install_requires = ['sqlalchemy', 'bcrypt', 'pyjwt', 'jinja2', 'cryptography', 'python-magic', 'watchdog', 'yarl'],
    extra_requires = {
        'develop': ['pytest']
    },
    use_scm_version = True,
    setup_requires = [
        'setuptools_scm'
    ],
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
