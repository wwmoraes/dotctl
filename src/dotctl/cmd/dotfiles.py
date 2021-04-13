#!/usr/bin/env python3

import os
import sys

from multiprocessing import get_start_method, set_start_method

import click

from dotctl import __version__
from dotctl.manager import Manager
from dotctl.privileges import elevate

DOTFILES_PATH = os.path.expanduser(os.environ.get("DOTFILES_PATH", "~/.files"))


@click.group()
@click.version_option(__version__, "-V", "--version")
@click.help_option("-h", "--help")
def main():
  if get_start_method(allow_none=False) != "spawn":
    set_start_method("spawn", force=True)
  if not os.path.exists(DOTFILES_PATH):
    print(f"{DOTFILES_PATH} does not exist", file=sys.stderr)
    sys.exit(1)


@main.command()
def install():
  """links the dot files into the home folder"""
  files = Manager(DOTFILES_PATH)
  files.install()


@main.command()
def setup():
  """executes setup scripts within the dot files path"""
  elevate("dotfiles")
  files = Manager(DOTFILES_PATH)
  files.setup()


if __name__ == "__main__":
  main()
