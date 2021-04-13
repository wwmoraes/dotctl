from subprocess import CompletedProcess
from typing import List
from dotctl.installers.installer import Installer
import shutil
from functools import cached_property


class Cargo(Installer):

  @property
  def base_cmd(self) -> List[str]:
    return ["cargo", "-q"]

  @property
  def install_cmd(self) -> List[str]:
    return ["install"]

  @property
  def uninstall_cmd(self) -> List[str]:
    return ["uninstall"]

  def is_installed(self, package: str, binary: str = None) -> bool:
    return shutil.which(binary or package) is not None


class Rustup(Installer):

  def __init__(self) -> None:
    super().__init__()
    targets = self.__cmd__(
      [*self.base_cmd, "target", "list", "--installed"],
      capture=True,
    )
    self.target = targets.stdout.splitlines()[0]

  @property
  def base_cmd(self) -> List[str]:
    return ["rustup"]

  @property
  def install_cmd(self) -> List[str]:
    return ["component", "add", "--target", self.target]

  @property
  def uninstall_cmd(self) -> List[str]:
    return ["component", "remove", "--target", self.target]

  @cached_property
  def list(self) -> List[str]:
    list_process = self.__cmd__(
      [*self.base_cmd, "component", "list", "--installed"],
      capture=True,
    )
    return sorted(list_process.stdout.splitlines())

  def is_installed(self, package: str, binary: str = None) -> bool:
    return (binary or f"{package}-{self.target}") in self.list
