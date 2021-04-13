import os

from multiprocessing import Process
from typing import List, Sequence

from dotctl import AnyPathLike
from dotctl.context import Context
from dotctl.manager import Manager
from dotctl.scripts import Packages, messages

from tests.fixtures.bin_mock import BinMock


class SetupScript():
  context: Context
  script_file: str
  script_name: str
  commands: List[str]
  outputs: List[str]
  bin_mock: BinMock

  @staticmethod
  def run_setup_script(script: str):
    setup = Manager.get_setup_fn(script)
    setup()

  def __init__(
    self,
    dir: AnyPathLike,
    script_file: str,
    packages_file: str,
    script_name: str,
    bin_mock: BinMock,
    bins: Sequence[str],
  ) -> None:
    self.context = Context(os.path.realpath(dir))
    self.context.update_environment()
    self.packages = Packages(self.context.SETUP_PATH, packages_file)
    self.script_file = script_file
    self.script_name = script_name
    self.commands = []
    self.outputs = []
    self.bin_mock = bin_mock
    for bin in bins:
      self.bin_mock.set_echo(bin)

  def add_expected_command(self, command: str):
    self.commands.append(command)

  def add_expected_output(self, output: str):
    self.outputs.append(output)

  def expected_output(self) -> str:
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
    return "\n".join([
      *self.commands,
      messages.script(self.script_name),
      *self.outputs,
      "",
    ])

  def execute(self) -> Process:
    script_path = os.path.join(self.context.SETUP_PATH, self.script_file)
    with self.bin_mock:
      process = Process(
        target=SetupScript.run_setup_script, args=(script_path,)
      )
      process.start()
      process.join()

    return process
