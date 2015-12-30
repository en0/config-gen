#!/usr/bin/env python2

from setuptools import setup

setup(
    name="config-gen",
    version="0.1",
    packages=['config_gen'],
    description="Configuration Generation using templates.",
    author="Ian Laird",
    author_email="en0@mail.com",
    url="https://github.com/en0/config-gen/",
    install_requires=['jinja2'],
    entry_points={
        'console_scripts': [
            'config-gen = config_gen.__main__:main',
            'cfgen = config_gen.__main__:cfgen'
        ]
    }
)
