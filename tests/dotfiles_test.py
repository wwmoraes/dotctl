import os
import sys
import subprocess

from tests.fixtures.script_output import ScriptOutput
from tests.fixtures.bin_mock import BinMock
import pytest
from pytest_mock import MockerFixture
from dotctl.scripts import messages
from colorama import Fore, Style
from pathlib import Path
from dotctl.context import Context, ContextInfo


@pytest.mark.integration
def test_install(
  bin_mock: BinMock,
  capfd: pytest.CaptureFixture[str],
  mocker: MockerFixture,
  script_output: ScriptOutput,
):
  mocker.patch.object(sys, "argv", ["", "install"])
  bin_mock.set_echo("stow")

  from dotctl.cmd.dotfiles import main
  bin_mock.activate()
  main(standalone_mode=False)
  bin_mock.deactivate()

  script_output.add_output(
    messages.success(
      f"stow {Fore.LIGHTBLUE_EX}global{Style.RESET_ALL} {messages.package('sample')}"
    )
  )
  script_output.add_output(
    "stow -d %s -t %s -R %s" % (
      os.environ.get("DOTFILES_PATH"),
      os.environ.get("HOME"),
      "sample",
    )
  )
  script_output.add_output("")

  captured = capfd.readouterr()
  assert captured.err == "", "stderr should be empty"
  assert captured.out == script_output.get(), "stdout does not match"


@pytest.mark.integration
def test_setup(
  bin_mock: BinMock,
  capfd: pytest.CaptureFixture[str],
  mocker: MockerFixture,
):
  # configure environment
  context = Context(os.environ.get("DOTFILES_PATH"))
  context.update_environment()
  mocker.patch.object(sys, "argv", ["", "setup"])
  mocked = mocker.patch("os.execlp")
  bin_mock.set_echo("brew")
  bin_mock.set_echo("sudo")
  # generate expected output
  test_output = ScriptOutput()
  test_output.set_script_name("Test packages")
  for package_info in [{
    "package": "echo",
    "installed": True
  }, {
    "package": "foo",
    "installed": False
  }, {
    "package": "bar",
    "installed": True
  }, {
    "package": "baz",
    "installed": False
  }]:
    test_output.add_output(
      "checking %s..." % messages.package(package_info["package"])
    )
    if not package_info["installed"]:
      test_output.add_command("install %s" % package_info["package"])
      test_output.add_output(
        "installing %s..." % messages.package(package_info["package"])
      )
  noop_output = ScriptOutput()
  noop_output.set_script_name("no-op")
  noop_output.add_output("NOOP!")
  privileged_output = ScriptOutput()
  privileged_output.set_script_name("Privileged settings")
  user_result = subprocess.run(["id", "-un"], capture_output=True, text=True)
  privileged_output.add_command(user_result.stdout.strip())
  group_result = subprocess.run(["id", "-gn"], capture_output=True, text=True)
  privileged_output.add_command(group_result.stdout.strip())
  brew_output = ScriptOutput()
  brew_output.set_script_name("Brew cask packages")
  for package in ["foo", "bar", "baz"]:
    brew_output.add_command("brew install -q --cask %s" % package)
    brew_output.add_output("checking %s..." % messages.package(package))
    brew_output.add_output("installing %s..." % messages.package(package))
    pass
  expected_output = "".join([
    test_output.get(),
    noop_output.get(),
    privileged_output.get(),
    brew_output.get(),
  ])
  # execute dotfiles setup with mocked binaries
  from dotctl.cmd.dotfiles import main
  bin_mock.activate()
  with pytest.raises(SystemExit) as exc:
    main(standalone_mode=False)
  bin_mock.deactivate()
  # check if elevate was called
  mocked.assert_not_called()
  # mocked.assert_called_once_with(
  #   "sudo",
  #   *[
  #     "%s=%s" % (key, os.environ.get(key, ""))
  #     for key in ContextInfo.__annotations__.keys()
  #   ],
  #   "--",
  #   sys.executable,
  #   "-m",
  #   "dotctl.cmd.dotfiles",
  #   "setup",
  # )
  captured = capfd.readouterr()

  assert exc.type == SystemExit, "unexpected exception type"
  assert exc.value.code == 0, "wrong exit code"
  assert captured.err == "", "stderr should be empty"
  assert captured.out == expected_output, "stdout does not match"


@pytest.mark.unit
def test_invalid_path(
  capfd: pytest.CaptureFixture[str],
  mocker: MockerFixture,
  tmp_path: Path,
):
  DOTFILES_PATH = os.path.join(tmp_path, "non-existent")
  os.environ.update({"DOTFILES_PATH": DOTFILES_PATH})
  mocker.patch.object(sys, "argv", ["", "install"])

  from dotctl.cmd import dotfiles
  # modules are cached, so we mock its global variables after the import.
  # Why not remove it from sys.modules or reload with importlib.reload?
  # Because both approaches have multiple caveats, specially when dealing with
  # imports between modules and global variables. This makes both solutions
  # unreliable for testing purposes. Caveats' references:
  # https://docs.python.org/3/library/importlib.html#importlib.reload
  # http://pyunit.sourceforge.net/notes/reloading.html
  mocker.patch.object(dotfiles, "DOTFILES_PATH", DOTFILES_PATH)
  with pytest.raises(SystemExit) as exc:
    dotfiles.main(standalone_mode=False)

  assert exc.type == SystemExit, "unexpected exception type"
  assert exc.value.code == 1, "wrong exit code"
  captured = capfd.readouterr()
  assert captured.err == f"{DOTFILES_PATH} does not exist\n", "stderr does not match"
  assert captured.out == "", "stdout should be empty"
