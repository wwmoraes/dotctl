import os
import pathlib
from dotctl.scripts import messages
from pytest import CaptureFixture
from tests.fixtures.bin_mock import BinMock

from tests.helpers.setup_script import SetupScript


def test_script(
  capfd: CaptureFixture[str],
  bin_mock: BinMock,
):
  setup_script = SetupScript(
    dir="tests/dotfiles",
    script_file="11-cask.py",
    packages_file="cask.txt",
    script_name="Brew cask packages",
    bin_mock=bin_mock,
    bins=("brew",),
  )
  for package in setup_script.packages:
    setup_script.add_expected_output(
      "checking %s..." % messages.package(package)
    )
    setup_script.add_expected_output(
      "installing %s..." % messages.package(package)
    )
    setup_script.add_expected_command("brew install -q --cask %s" % package)

  process = setup_script.execute()

  assert process.exitcode == 0
  captured = capfd.readouterr()
  assert captured.err == "", "stderr is not empty"

  assert captured.out == setup_script.expected_output(), "stdout does not match"
