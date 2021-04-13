import os

from multiprocessing import Process
from typing import Protocol

import pytest

from dotctl.context import Context
from dotctl.manager import Manager


def run_setup_script(script: str):
  setup = Manager.get_setup_fn(script)
  setup()


class ScriptProcess(Protocol):
  """configures a Context and creates a script Process instance"""

  def __call__(self, basepath: str, scriptpath: str) -> Process:
    """creates the `scriptpath` script process within the `basepath` context

    `basepath` is used as Context's dotfiles root directory, which will be set
    on the environment prior to the script execution. The `scriptpath` must be
    relative to the `basepath`.
    """
    ...


@pytest.fixture
def script_process() -> ScriptProcess:

  def run(basepath: str, scriptpath: str) -> Process:
    context = Context(os.path.realpath(basepath))
    context.update_environment()

    script_path = os.path.realpath("%s/%s" % (basepath, scriptpath))
    return Process(target=run_setup_script, args=(script_path,))

  return run
