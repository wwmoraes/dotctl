import os
import json
from typing import List, TypedDict
from dotctl import AnyPathLike, platform


class ContextInfo(TypedDict):
  ARCH: str
  DOTFILES_PATH: str
  HOST: str
  PACKAGES_PATH: str
  SETUP_PATH: str
  SYSTEM: str
  TAGS: str


class Context:
  """environment information about the current host"""

  @staticmethod
  def from_env() -> ContextInfo:
    """load context information from environment variables"""
    context: ContextInfo = ContextInfo(
      **{key: os.getenv(key, "") for key in ContextInfo.__annotations__.keys()}
    )
    return context

  def __init__(self, dir: AnyPathLike) -> None:
    if not os.path.isdir(dir):
      raise RuntimeError("%r is not a valid directory" % dir)

    self.DOTFILES_PATH: str = str(dir)
    self.SETUP_PATH: str = os.path.join(self.DOTFILES_PATH, ".setup.d")
    self.PACKAGES_PATH: str = os.path.join(
      self.DOTFILES_PATH, ".setup.d", "packages"
    )
    self.ARCH: str = (os.environ.get("ARCH") or platform.machine()).lower()
    self.SYSTEM: str = (os.environ.get("SYSTEM") or platform.system()).lower()
    self.HOST: str = platform.hostname()

    TAGSRC = os.path.expanduser(os.environ.get("TAGSRC") or "~/.tagsrc")
    if not os.path.isfile(TAGSRC):
      self.TAGS = ""
      return
    with open(TAGSRC, "r") as tags:
      self.TAGS = ",".join(tags.read().strip().splitlines())

  def update_environment(self) -> None:
    os.environ.update({
      "DOTFILES_PATH": self.DOTFILES_PATH,
      "SETUP_PATH": self.SETUP_PATH,
      "PACKAGES_PATH": self.PACKAGES_PATH,
      "ARCH": self.ARCH,
      "SYSTEM": self.SYSTEM,
      "HOST": self.HOST,
      "TAGS": self.TAGS,
    })
