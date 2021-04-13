from dotctl.installers.installer import Installer
import shutil


class Yarn(Installer):

  @property
  def base_cmd(self):
    return ["yarn", "global"]

  @property
  def install_cmd(self):
    return ["add"]

  @property
  def uninstall_cmd(self):
    return ["remove"]

  def is_installed(self, package: str, binary: str = None) -> bool:
    return shutil.which(binary or package) is not None
