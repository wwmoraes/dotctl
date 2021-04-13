from functools import cached_property
from typing import List
from dotctl.installers.installer import Installer


class Python3Pip(Installer):

  @property
  def base_cmd(self):
    return ["python", "-m", "pip"]

  @property
  def install_cmd(self):
    return ["install", "-qqq"]

  @property
  def uninstall_cmd(self):
    return ["uninstall"]

  @cached_property
  def list(self) -> List[str]:
    list_process = self.__cmd__(
      [*self.base_cmd, "list", "--format", "freeze"],
      capture=True,
    )
    entries = list_process.stdout.splitlines()
    return sorted([entry.split("=")[0] for entry in entries])

  def is_installed(self, package: str, binary: str = None) -> bool:
    return (binary or package) in self.list
