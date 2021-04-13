import os
import tempfile
from typing import Callable
from sys import exit, stderr
from dotctl.scripts import messages
from dotctl.privileges import demote
import traceback
import shutil

SetupFn = Callable[[], None]


def dotsetup(
  *,
  name: str,
  root: bool = False,
  debug: bool = False,
  catch_exceptions: bool = True,
) -> Callable[[SetupFn], SetupFn]:
  """decorates dotctl script setup functions

  adds messages and error handling to prevent interruptions
  """

  def decorator(fn: SetupFn) -> SetupFn:

    def wrapper() -> None:
      try:
        if not root:
          demote()
        # second try block to ensure we cleanup the temp dir & change back
        try:
          print(messages.script(name))
          OLD_DIR = os.path.realpath(os.curdir)
          TMP_DIR = tempfile.mkdtemp()
          os.chmod(TMP_DIR, 0o0750)  # nosec
          os.chdir(TMP_DIR)
          fn()
        finally:
          os.chdir(OLD_DIR)
          # both os.rmdir and shutil fail to delete, even if we grant broad
          # privileges to the temporary folder, so we abuse sudo to "recover"
          # the privileges from a demote, and clean up after ourselves properly
          shutil.rmtree(TMP_DIR, ignore_errors=True)
      except Exception as err:
        if not catch_exceptions:
          raise
        if debug:
          traceback.print_exc()
        print(str(err), file=stderr)
        exit(1)

    return wrapper

  return decorator
