#!/usr/bin/python

from setuptools import find_packages, setup

setup(
    name="mitama",
    install_requires=[
        "sqlalchemy",
        "bcrypt",
        "pyjwt",
        "jinja2",
        "cryptography",
        "python-magic",
        "watchdog",
        "yarl",
        "pysaml2",
        "tzlocal",
    ],
    extra_requires={"develop": ["unittest", "flake8", "isort", "black"]},
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(),
    package_data={
        "mitama.portal": [
            "templates/*.html",
            "templates/**/*.html",
            "static/*",
        ],
        "mitama.http": [
            "templates/*.html",
        ],
        "mitama.app": [
            "static/*",
        ],
        "mitama": [
            "skeleton/*",
            "skeleton/**/*",
            "skeleton/**/**/*",
        ],
    },
    entry_points={"console_scripts": ["mitama = mitama.commands:exec"]},
)
