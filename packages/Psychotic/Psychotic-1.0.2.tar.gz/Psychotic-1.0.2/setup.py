# -*- coding: UTF-8 -*-

#from setuptools import setup, find_packages
from distutils.core import setup
import sys, os

setup(
    name='Psychotic',
    version="1.0.2",
    description="Cross-platform pure Python performance optimizer and 2008 April Fools joke.",
    classifiers=[],
    author="Kevin Dangoor",
    author_email="dangoor@gmail.com",
    url="http://psychotic.googlecode.com/",
    license="BSD",
    packages=["psychotic"],
    modules=["fact.py", "sort.py"]
)
