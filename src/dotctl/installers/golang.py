from typing import List
from dotctl.installers.installer import Installer
import shutil


class GoMod(Installer):

  @property
  def base_cmd(self) -> List[str]:
    return ["go"]

  @property
  def install_cmd(self) -> List[str]:
    return ["get"]

  @property
  def uninstall_cmd(self) -> List[str]:
    raise NotImplementedError()

  def is_installed(self, package: str, binary: str = None) -> bool:
    return shutil.which(binary or package) is not None
