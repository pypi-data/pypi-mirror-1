#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools()
from os import path
from setuptools import setup, find_packages

VERSION = open(path.join(path.dirname(__file__), 'VERSION')).read().strip()

setup(
    name = "django-renderform",
    version = VERSION,
    url = "http://code.google.com/p/django-renderform/",
    author = "Brian Beck",
    author_email = "exogen@gmail.com",
    license = "MIT License",
    description = "Helpers for rendering Django forms in a flexible way.",
    packages = ['renderform'],
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ]
)
