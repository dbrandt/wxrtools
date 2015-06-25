#!/usr/bin/env python
from setuptools import setup, find_packages


kwargs = {
    "name": "wxrtools",
    "version": "0.1-prerelease",
    "description": "Package for handling WordPress export format (WXR)",
    "author": "Daniel Brandt",
    "author_email": "me@dbrandt.se",
    "url": "http://dbrandt.se/wxrtools",
    "scripts": ["bin/wxrtool.py"],
    "packages": find_packages(),
    "install_requires": [l.strip() for l in open("requirements.txt").readlines()],
}

if __name__ == "__main__":
    setup(**kwargs)
