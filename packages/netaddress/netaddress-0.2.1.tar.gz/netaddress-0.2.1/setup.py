#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="netaddress",
    version="0.2.1",
    description="Validating parser for URI's (RFC 3986)",
    author="Vincent Kraeutler",
    author_email="vincent@kraeutler.net",
    url="http://www.kraeutler.net/vincent/pub/netaddress",
    license="BSD License",
    packages=find_packages('src'),
    package_dir={
                 '' : 'src'
                },
    install_requires = ["pyparsing>=1.4.7"],
    zip_safe=False,
)
