import os
import sys

from multiprocessing import get_start_method, set_start_method

from dotenv import load_dotenv

pytest_plugins = (
  "tests.fixtures.bin_mock",
  "tests.fixtures.script_process",
  "tests.fixtures.script_output",
)


def pytest_runtest_setup():
  if get_start_method(allow_none=True) is None:
    set_start_method("spawn")
  persistent = {
    key: os.environ.get(key, "") for key in [
      "PATH",
      "HOME",
      "USER",
      "SUDO_USER",
      "SUDO_GID",
      "SUDO_UID",
    ]
  }
  os.environ.clear()
  os.environ.update(persistent)
  load_dotenv(".env", verbose=True)
  load_dotenv(".env.test", verbose=True)
  # replace relative paths with absolute ones
  for key in ["HOME", "DOTFILES_PATH", "DOTSECRETS_PATH"]:
    value = os.environ.get(key)
    if value is None:
      continue
    os.environ[key] = os.path.realpath(value)
