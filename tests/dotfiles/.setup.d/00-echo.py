from typing import List, Optional
from functools import cached_property

from dotctl.installers.installer import Installer
from dotctl.scripts import dotsetup, messages


class Echo(Installer):
  installed: List[str]

  def __init__(self, installed: Optional[List[str]] = None) -> None:
    super().__init__()
    self.installed = installed or []

  @property
  def base_cmd(self) -> List[str]:
    return ["echo"]

  @property
  def install_cmd(self) -> List[str]:
    return ["install"]

  @property
  def uninstall_cmd(self) -> List[str]:
    return ["remove"]

  @cached_property
  def list(self) -> List[str]:
    return sorted(self.installed)

  def is_installed(self, package: str, binary: str = None) -> bool:
    return (binary or package) in self.list


@dotsetup(name="Test packages")
def setup() -> None:
  installer = Echo(["echo", "bar"])
  packages = ["echo", "foo", "bar", "baz"]
  for package in packages:
    print(f"checking {messages.package(package)}...")
    if installer.is_installed(package):
      continue
    print(f"installing {messages.package(package)}...")
    installer.install(package)


if __name__ == "__main__":
  setup()
