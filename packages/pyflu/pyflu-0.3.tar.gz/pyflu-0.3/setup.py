#!/usr/bin/env python

from setuptools import setup, find_packages, Extension
from pyflu import version
from pyflu.setuptools.versioning import GitReleaseCommand


class PyfluReleaseCommand(GitReleaseCommand):
    defaults = {
        "version": version(),
        "name": "pyflu",
    }


setup(
    name = "pyflu",
    version = version(),
    author = "Luper Rouch",
    author_email = "luper.rouch@gmail.com",
    maintainer = "Luper Rouch",
    maintainer_email = "luper.rouch@gmail.com",
    url = "http://projects.luper.fr/misc/wiki/pyflu",
    description = "A collection of Python utilities.",
    longer_description = "Mainly helpers for standard Python modules, " \
            "things that I frequently use in my projects.",

    install_requires = ["lxml"],

    packages = find_packages(),    
    cmdclass = {
        "release": PyfluReleaseCommand,
    },    
)
