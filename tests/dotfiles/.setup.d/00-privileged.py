import subprocess
import os
from dotctl.scripts import dotsetup, messages
import platform


@dotsetup(name="Privileged settings", root=True)
def setup() -> None:
  # subprocess.run(["cat", "/etc/sudoers"], capture_output=False)
  os.system("id -un")
  os.system("id -gn")


if __name__ == "__main__":
  setup()
