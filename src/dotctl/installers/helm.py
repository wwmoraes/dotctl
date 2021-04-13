from subprocess import CompletedProcess
from typing import List
from dotctl.installers.installer import Installer
import shutil
from functools import cached_property


class HelmPlugin(Installer):

  @property
  def base_cmd(self) -> List[str]:
    return ["helm", "plugin"]

  @property
  def install_cmd(self) -> List[str]:
    return ["install"]

  @property
  def uninstall_cmd(self) -> List[str]:
    return ["uninstall"]

  @cached_property
  def list(self) -> List[str]:
    list_process = self.__cmd__(
      [*self.base_cmd, "list"],
      capture=True,
    )
    return sorted([
      line.split("\t")[0] for line in list_process.stdout.splitlines()[1:]
    ])

  def is_installed(self, package: str) -> bool:
    return package in self.list
