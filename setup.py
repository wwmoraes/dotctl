#!/usr/bin/env python

import setuptools

import importlib

metaspec = importlib.util.spec_from_file_location(
  "meta", "src/dotctl/__init__.py"
)
__version__ = metaspec.loader.load_module("meta").__version__

with open("README.md", "r", encoding="utf-8") as fh:
  long_description = fh.read()

setuptools.setup(
  name="dotctl",
  version=__version__,
  license="MIT",
  author="William Artero",
  author_email="william@artero.dev",
  description="cross-system customization using dot files",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/wwmoraes/dotctl",
  project_urls={
    "Bug Tracker": "https://github.com/wwmoraes/dotctl/issues",
  },
  platforms=[
    "MacOS X",
    "Linux",
    # "Windows",
  ],
  classifiers=[
    "Development Status :: 1 - Planning",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    # "Operating System :: Microsoft :: Windows",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Topic :: System :: Installation/Setup",
    "Topic :: Utilities",
  ],
  keywords="dotfiles package-installer stow preferences packages sync",
  package_dir={"": "src"},
  packages=setuptools.find_packages(where="src"),
  entry_points={
    "console_scripts": [
      "dotfiles = dotctl.cmd.dotfiles:main",
      "dotsecrets = dotctl.cmd.dotsecrets:main",
      "dotrun = dotctl.cmd.dotrun:main",
    ]
  },
  python_requires=">=3.6",
)
