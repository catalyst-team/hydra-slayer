#!/usr/bin/env python
# -*- coding: utf-8 -*-
# flake8: noqa

from typing import Union
from pathlib import Path

from setuptools import find_packages, setup

# Package meta-data.
NAME = "hydra-slayer"
DESCRIPTION = (
    "Hydra Slayer is a 4th level spell in the School of Fire Magic."
    " Depending of the level of expertise in fire magic,"
    " slayer spell increases attack of target troop by 8"
    " against hydras, snakes (e.g., pythons), and other creatures."
)
URL = "https://github.com/catalyst-team/hydra-slayer"
EMAIL = ""
AUTHOR = ""
REQUIRES_PYTHON = ">=3.6.0"

PROJECT_ROOT = Path(__file__).parent.resolve()


def load_requirements(filename: Union[Path, str]):
    with open(PROJECT_ROOT / filename) as f:
        return f.read().splitlines()


def load_readme(filename: Union[Path, str]):
    with open(PROJECT_ROOT / filename, encoding="utf-8") as f:
        return f"\n{f.read()}"


def load_version(filename: Union[Path, str]):
    context = {}
    with open(PROJECT_ROOT / filename) as f:
        exec(f.read(), context)
    return context["__version__"]


setup(
    name=NAME,
    version=load_version(Path("hydra_slayer", "__version__.py")),
    description=DESCRIPTION,
    long_description=load_readme("README.md"),
    long_description_content_type="text/markdown",
    keywords=["Distributed Computing"],
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    download_url=URL,
    project_urls={},
    packages=find_packages(exclude=("tests",)),
    entry_points={},
    scripts=[],
    install_requires=load_requirements(Path("requirements", "requirements.txt")),
    extras_require={},
    include_package_data=True,
    license="Apache License 2.0",
    classifiers=[
        "Environment :: Console",
        "Natural Language :: English",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        # Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        # Topics
        "Topic :: Scientific/Engineering :: Information Analysis",
        # Programming
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
