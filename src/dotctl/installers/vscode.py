from subprocess import CompletedProcess
from typing import List
from dotctl.installers.installer import Installer
import shutil
from functools import cached_property


class VSCodeExtension(Installer):

  @property
  def base_cmd(self) -> List[str]:
    return ["code"]

  @property
  def install_cmd(self) -> List[str]:
    return ["--install-extension"]

  @property
  def uninstall_cmd(self) -> List[str]:
    return ["--uninstall-extension"]

  @cached_property
  def list(self) -> List[str]:
    list_process = self.__cmd__(
      [*self.base_cmd, "--list-extensions"],
      capture=True,
    )
    return sorted(list_process.stdout.lower().splitlines())

  def is_installed(self, package: str) -> bool:
    return package in self.list
