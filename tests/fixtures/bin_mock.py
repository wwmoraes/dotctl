from typing import List, Optional, Type
from types import TracebackType
import pytest
import pathlib
import os
import inspect


class BinMock():
  """mock binaries' manager

  uses the provided directory to create mocked binaries at. Those binaries can
  then be used either by:

  * using the instance as a context (i.e. `with`)
  * toggling the mocks manually with activate/deactivate methods

  Both options will modify the PATH environment variable, and prepend/remove
  the directory managed by the instance.

  NOTE: The provided directory tree must be accessible by the target user,
  otherwise the mocks won't be accessible!
  """

  def __init__(
    self,
    dir: str,
  ) -> None:
    self.dir = dir

  def __enter__(self):
    self.activate()

  def __exit__(
    self,
    type: Optional[Type[BaseException]],
    value: Optional[BaseException],
    traceback: Optional[TracebackType],
  ):
    self.deactivate()
    if (type, value, traceback) != (None, None, None):
      raise

  def activate(self):
    PATH = os.environ.get("PATH", "").split(":")
    # makes sure the same path is set only once, and at the beginning
    while self.dir in PATH:
      PATH.remove(self.dir)
    PATH.insert(0, self.dir)
    os.environ.update(PATH=":".join(PATH))

  def deactivate(self):
    PATH = os.environ.get("PATH", "").split(":")
    while self.dir in PATH:
      PATH.remove(self.dir)
    os.environ.update(PATH=":".join(PATH))

  def set_echo(self, bin_name: str):
    bin_path = os.path.join(self.dir, bin_name)
    with open(bin_path, "w+") as f:
      f.write(
        inspect.cleandoc(
          """
        #!/usr/bin/env python

        import os
        import sys

        print(os.path.basename(sys.argv[0]), *sys.argv[1:])
        """
        )
      )
    os.chmod(bin_path, mode=0o0755)


@pytest.fixture
def bin_mock(tmp_path: pathlib.Path) -> BinMock:
  """generates a BinMock instance using a pytest tmp_path

  The tmp_path permissions will be changed to allow both group and others access
  so the mocks work regardless of the user that tries to use them.
  """

  # The tmp_path fixture creates a temporary path tree with 0700 permissions at
  # <tmp>/pytest-of-<user>/pytest-<N>/<test-name><N>. We must change these
  # permissions to make the complete tree executable by any user, making it
  # accessible by demoted processes
  real_path = os.path.realpath(tmp_path)
  base_path = os.path.realpath(os.path.join(real_path, "../../"))
  os.chmod(base_path, 0o0755)
  for root, dirs, files in os.walk(base_path):
    for entry in dirs:
      os.chmod(os.path.join(root, entry), 0o0755)
    for entry in files:
      entry_path = os.path.join(root, entry)
      if os.access(entry_path, os.X_OK):
        os.chmod(entry_path, 0o0755)
      else:
        os.chmod(entry_path, 0o0644)
  return BinMock(real_path)
