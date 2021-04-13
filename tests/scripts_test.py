import os

from multiprocessing import Process

from pytest import CaptureFixture

from dotctl.context import Context
from dotctl.manager import Manager, run_setup_script
from dotctl.scripts import messages


def test_script(capfd: CaptureFixture[str]):
  context = Context(os.path.realpath("tests/dotfiles"))
  context.update_environment()

  script_path = os.path.realpath("tests/dotfiles/.setup.d/00-echo.py")
  process = Process(target=run_setup_script, args=(script_path,))
  process.start()
  process.join()

  assert process.exitcode == 0
  captured = capfd.readouterr()
  assert captured.err == "", "error output is not empty"
  # captured output is out-of-order due to how pytest handles [sub]processes.
  # Both Process and subprocess instances use Popen under the hood, which is
  # buffered and is only captured after the process exits. Installer classes
  # uses a subprocess.run to execute commands, and the whole setup script is
  # executed as a Process. That means a sample process tree for a script is:
  #
  #   Process X [script]
  #     subprocess.run 1 [list, if configured]
  #     subprocess.run 2 [install/uninstall package 1]
  #     subprocess.run N [install/uninstall package N]
  #
  # the captured output, as seen by pytest, will then be:
  #
  #   subprocess.run 1 [list, if configured]
  #   subprocess.run 2 [install/uninstall package 1]
  #   subprocess.run N [install/uninstall package N]
  #   Process X [script]
  #

  assert captured.out == "\n".join([
    "install foo",
    "install baz",
    messages.script("Test packages"),
    "checking %s..." % messages.package("echo"),
    "checking %s..." % messages.package("foo"),
    "installing %s..." % messages.package("foo"),
    "checking %s..." % messages.package("bar"),
    "checking %s..." % messages.package("baz"),
    "installing %s..." % messages.package("baz"),
    "",
  ]), "script output does not match"
