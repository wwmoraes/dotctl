#!/usr/bin/env python3

import os
import sys

from multiprocessing import get_start_method, set_start_method

import click

from dotctl import __version__
from dotctl.manager import Manager
from dotctl.privileges import elevate

# we cannot use the environ.get with the default value parameter as an empty
# string does not fallback to it.
DOTFILES_PATH = os.path.expanduser(
  os.environ.get("DOTFILES_PATH") or "~/.files"
)
DOTSECRETS_PATH = os.path.expanduser(
  os.environ.get("DOTSECRETS_PATH") or "~/.secrets"
)


@click.group()
@click.version_option(__version__, "-V", "--version", prog_name="dotctl")
@click.help_option("-h", "--help")
def main():
  """cross-system customization using dot files"""
  if get_start_method(allow_none=False) != "spawn":
    set_start_method("spawn", force=True)


@main.group()
def files():
  """interact with file packages and scripts only"""
  if not os.path.exists(DOTFILES_PATH):
    print(f"{DOTFILES_PATH} does not exist", file=sys.stderr)
    sys.exit(1)


@files.command(name="install")
def files_install():
  """stows packages into the home folder"""
  files = Manager(DOTFILES_PATH)
  files.install()


@files.command(name="setup")
def files_setup():
  """executes setup scripts"""
  elevate("dotctl")
  files = Manager(DOTFILES_PATH)
  files.setup()


@main.group()
def secrets():
  """interact with secret packages and scripts only"""
  if not os.path.exists(DOTSECRETS_PATH):
    print(f"{DOTSECRETS_PATH} does not exist", file=sys.stderr)
    sys.exit(1)


@secrets.command(name="install")
def secrets_install():
  """stows packages into the home folder"""
  secrets = Manager(DOTSECRETS_PATH)
  secrets.install()


@secrets.command(name="setup")
def secrets_setup():
  """executes setup scripts"""
  elevate("dotctl")
  secrets = Manager(DOTSECRETS_PATH)
  secrets.setup()


@main.command()
@click.pass_context
def install(ctx: click.Context):
  """stows both file and secret packages into the home folder"""
  ctx.invoke(files)
  ctx.invoke(secrets)
  ctx.invoke(files_install)
  ctx.invoke(secrets_install)


@main.command()
@click.pass_context
def setup(ctx: click.Context):
  """runs both file and secret setup scripts"""
  elevate("dotctl")
  ctx.invoke(files)
  ctx.invoke(secrets)
  ctx.invoke(files_setup)
  ctx.invoke(secrets_setup)


if __name__ == "__main__":
  main()
