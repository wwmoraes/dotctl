from abc import ABC, abstractmethod
import subprocess
from typing import List, Literal, Sequence, Union, final, overload
import shutil
import os
from dotctl.privileges import demote

CompletedCmdBytes = subprocess.CompletedProcess[bytes]
CompletedCmdStr = subprocess.CompletedProcess[str]
CompletedCmd = Union[CompletedCmdBytes, CompletedCmdStr]


class Installer(ABC):

  @overload
  @staticmethod
  def __cmd__(
    cmd: Sequence[str],
    *args,
    capture: Literal[True],
    as_user: bool = False,
    **kwargs,
  ) -> CompletedCmdStr:
    ...

  @overload
  @staticmethod
  def __cmd__(
    cmd: Sequence[str],
    *args,
    capture: Literal[False],
    as_user: bool = False,
    **kwargs,
  ) -> CompletedCmdBytes:
    ...

  @overload
  @staticmethod
  def __cmd__(
    cmd: Sequence[str],
    *args,
    capture: bool = False,
    as_user: bool = False,
    **kwargs,
  ) -> CompletedCmdBytes:
    ...

  @staticmethod
  def __cmd__(
    cmd: Sequence[str],
    *args: str,
    capture: bool = False,
    as_user: bool = False,
    **kwargs
  ) -> CompletedCmd:
    kwargs = {
      **kwargs,
      "capture_output": capture,
      "text": capture,
      "preexec_fn": demote if as_user else None,
    }
    return subprocess.run(cmd, *args, **kwargs)

  @property
  @abstractmethod
  def base_cmd(self) -> List[str]:
    raise NotImplementedError()

  @property
  @abstractmethod
  def install_cmd(self) -> List[str]:
    raise NotImplementedError()

  @property
  @abstractmethod
  def uninstall_cmd(self) -> List[str]:
    raise NotImplementedError()

  def __init__(self) -> None:
    base_cmd = shutil.which(self.base_cmd[0])
    if not base_cmd:
      raise FileNotFoundError(self.base_cmd[0])
    self.base_cmd[0] = base_cmd

  @abstractmethod
  def is_installed(self, package: str) -> bool:
    raise NotImplementedError()

  @final
  def is_uninstall(self, package: str) -> bool:
    return package.startswith("-")

  @final
  def install(self, package: str, *args: str) -> CompletedCmd:
    if self.install_cmd is None:
      raise NotImplementedError("install command not set")
    return self.__cmd__([
      *self.base_cmd,
      *self.install_cmd,
      package.lstrip("-"),
      *args,
    ])

  @final
  def uninstall(self, package: str, *args: str) -> CompletedCmd:
    if self.uninstall_cmd is None:
      raise NotImplementedError("uninstall command not set")
    return self.__cmd__([
      *self.base_cmd,
      *self.uninstall_cmd,
      package.lstrip("-"),
      *args,
    ])
