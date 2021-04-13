import os
import sys
import shutil

from dotctl.context import Context, ContextInfo


def elevate(module: str):
  """elevates and replaces the current process if needed

  sudo is used and mandatory, as it is used during by the demote mechanism
  """

  # elevate right away
  if os.getuid() != 0 or os.getgid() != 0:
    return __elevate__(module)

  # check if the sudo environment variables are present,
  # otherwise demoting won't be possible
  if os.environ.get("SUDO_UID") is None:
    raise RuntimeError("please run as user using sudo")
  if os.environ.get("SUDO_GID") is None:
    raise RuntimeError("please run as user using sudo")


def __elevate__(module: str):
  context = Context.from_env()
  os.environ.update(context.items())

  # sudo -E/--preserve-env does not work: os.execv[e] (which is used under the
  # hood by os.execlp[e]) does not pass the environment properly to sudo.
  SUDO_BIN = shutil.which("sudo")
  if SUDO_BIN is None:
    raise RuntimeError("sudo binary not found on path")

  # TODO securely expand env and args
  os.execlp(
    SUDO_BIN,
    *["%s=%s" % (key, value) for (key, value) in context.items()],
    "--",
    sys.executable,
    "-m",
    f"dotctl.cmd.{module}",
    *sys.argv[1:],
  )


def demote():
  # we're already a non-root user
  if os.getuid() != 0 and os.getgid() != 0:
    return

  sudo_gid = os.environ.get("SUDO_GID")
  sudo_uid = os.environ.get("SUDO_UID")

  # check if the sudo environment variables are present,
  # otherwise demoting won't be possible
  if sudo_uid is None:
    raise RuntimeError("sudo UID not found - please run as user using sudo")
  if sudo_gid is None:
    raise RuntimeError("sudo GID not found - please run as user using sudo")

  target_gid = int(sudo_gid)
  target_uid = int(sudo_uid)

  os.setsid()
  os.setgroups([target_gid])
  os.setgid(target_gid)
  os.setuid(target_uid)


def assert_root():
  if os.getuid() != 0:
    raise RuntimeError("sudo UID not found - please run as user using sudo")
  if os.getgid() != 0:
    raise RuntimeError("sudo GID not found - please run as user using sudo")
