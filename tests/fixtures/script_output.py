from typing import List, Optional
import pytest
from dotctl.scripts import messages


class ScriptOutput():
  """generates pytest's capfd-compatible output for assertions"""

  script_name: Optional[str] = None
  commands: List[str]
  outputs: List[str]

  def __init__(self) -> None:
    self.commands = []
    self.outputs = []

  def set_script_name(self, script_name: str):
    self.script_name = script_name

  def add_command(self, command: str):
    self.commands.append(command)

  def add_output(self, output: str):
    self.outputs.append(output)

  def get(self) -> str:
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
      *([messages.script(self.script_name)] if self.script_name else []),
      *self.outputs,
      "",
    ])


@pytest.fixture
def script_output() -> ScriptOutput:
  return ScriptOutput()
