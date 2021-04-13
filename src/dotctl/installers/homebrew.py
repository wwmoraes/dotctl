from typing import List
from dotctl.installers.installer import Installer
from functools import cached_property
import shutil


class Formula(Installer):

  @property
  def base_cmd(self) -> List[str]:
    return ["brew"]

  @property
  def install_cmd(self) -> List[str]:
    return ["install", "--formula"]

  @property
  def uninstall_cmd(self) -> List[str]:
    return ["remove", "--formula"]

  def is_installed(self, package: str, binary: str = None) -> bool:
    return shutil.which(binary or package) is not None


class Cask(Installer):

  @property
  def base_cmd(self) -> List[str]:
    return ["brew"]

  @property
  def install_cmd(self) -> List[str]:
    return ["install", "-q", "--cask"]

  @property
  def uninstall_cmd(self) -> List[str]:
    return ["remove", "-q", "--cask"]

  def is_installed(self, package: str, binary: str = None) -> bool:
    return shutil.which(
      binary or f"/Applications/{package}.app/Contents/MacOS/{package}"
    ) is not None


class Tap(Installer):

  @property
  def base_cmd(self) -> List[str]:
    return ["brew", "tap"]

  @property
  def install_cmd(self) -> List[str]:
    return []

  @property
  def uninstall_cmd(self) -> List[str]:
    return super().uninstall_cmd

  @cached_property
  def list(self) -> List[str]:
    list_process = self.__cmd__(self.base_cmd, capture=True)
    return sorted(list_process.stdout.splitlines())

  def is_installed(self, package: str, bin: str = None) -> bool:
    return package in self.list
