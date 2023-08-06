try:
    import setuptools
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
from setuptools import setup, find_packages

import sys, os

libdir = "lib"

sys.path.insert(0, libdir)

import modhex as pkg

setup_options = {
    "name": "Modhex",
    "version": "0.1",
    "description": "Translate yubikey one-time passwords to modhex regardless of keyboard layout.",
    "long_description":file("README.txt", "r").read(),
    "author": "Daniel Holth",
    "author_email": "dholth@fastmail.fm",
    "packages": ['modhex'],
    "package_dir": {"": libdir},
    "include_package_data": True,
    "zip_safe": True,
}

setup(**setup_options)
