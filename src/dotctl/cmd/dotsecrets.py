#!/usr/bin/env python3

import os
import sys

from multiprocessing import get_start_method, set_start_method

import click

from dotctl import __version__
from dotctl.manager import Manager

DOTSECRETS_PATH = os.environ.get(
  "DOTSECRETS_PATH", os.path.expanduser("~/.secrets")
)


@click.group()
@click.version_option(__version__, "-V", "--version")
@click.help_option("-h", "--help")
def main():
  if get_start_method(allow_none=False) != "spawn":
    set_start_method("spawn", force=True)
  if not os.path.exists(DOTSECRETS_PATH):
    print(f"{DOTSECRETS_PATH} does not exist", file=sys.stderr)
    sys.exit(1)


@main.command()
def install():
  """links the dot secrets into the home folder"""

  files = Manager(os.path.expanduser(DOTSECRETS_PATH))
  files.install()


if __name__ == "__main__":
  main()
