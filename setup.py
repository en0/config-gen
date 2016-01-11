#!/usr/bin/env python2

from setuptools import setup

setup(
    name="config-gen",
    version="1.1",
    packages=['config_gen', 'config_gen.adapters'],
    description="Configuration Generation using templates.",
    author="Ian Laird",
    author_email="en0@mail.com",
    url="https://github.com/en0/config-gen/",
    install_requires=['jinja2', 'redis'],
    entry_points={
        'console_scripts': [
            'config-gen-init = config_gen.__main__:main_init',
            'config-gen-store = config_gen.__main__:main_ks',
            'config-gen-keys = config_gen.__main__:main_keys',
            'config-gen = config_gen.__main__:main_render',
        ]
    }
)
