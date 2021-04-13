import os
import sys

from multiprocessing import get_start_method, set_start_method, Process

import click

from dotctl.context import Context
from dotctl.manager import run_setup_script
from dotctl.privileges import elevate


@click.command()
@click.argument("script")
def main(script: str):
  if get_start_method(allow_none=False) != "spawn":
    set_start_method("spawn", force=True)
  elevate("dotrun")

  context = Context(
    os.path.expanduser(os.environ.get("DOTFILES_PATH") or "~/.files")
  )
  context.update_environment()

  process = Process(target=run_setup_script, args=(script,))
  process.start()
  process.join()


if __name__ == "__main__":
  main()
