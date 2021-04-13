import platform
import subprocess
import shutil
from typing import Callable, Dict

commonArch = {
  "armv8": "arm64",
  "arm64e": "arm64",
  "aarch64": "arm64",
  "x86_64": "amd64",
  "armv7": "arm",
  "armv6": "arm",
  "x86": "386",
}


def system() -> str:
  return platform.system().lower()


def node() -> str:
  return platform.node()


def hostname() -> str:
  return node().split(".")[0]


def _machine_darwin() -> str:
  if system() != "darwin":
    raise RuntimeError("machine_darwin should only be executed on Darwin")

  # sysctl brand info is set by the mach kernel
  result = subprocess.run(["sysctl", "-qn", "machdep.cpu.brand_string"],
                          capture_output=True,
                          text=True)

  if result.returncode != 0:
    return platform.machine()

  brand_string = result.stdout.strip().lower()
  if brand_string.startswith("apple m"):
    return "arm64e"
  elif brand_string.startswith("intel"):
    return "amd64"

  # fallback
  return platform.machine()


def _machine_linux() -> str:
  if system() != "linux":
    raise RuntimeError("machine_linux should only be executed on Linux")

  # lscpu gets the architecture from the sysfs
  if shutil.which("lscpu") is not None:
    result = subprocess.run(["lscpu"], capture_output=True, text=True)  # nosec
    for line in result.stdout.splitlines():
      if not line.startswith("Architecture:"):
        continue
      # safely try to extract the architecture's field value
      arch_info = line.split(" ", 1)[1] or None
      if arch_info is not None:
        # tidy up the value found
        return arch_info.strip().lower()
      else:
        # halt when an empty architecture field is found
        break

  # fallback
  return platform.machine()


# OS-specific machine function to execute
MACHINES: Dict[str, Callable[[], str]] = {
  "darwin": _machine_darwin,
  "linux": _machine_linux,
}


def machine() -> str:
  """returns the true architecture of this machine

  Python standard modules (such as os and platform) return the architecture the
  interpreter binary has been compiled to instead of the real architecture
  of the host. Both modules rely on the POSIX uname system call on unix systems,
  which sets the architecture at build time. Even though such behavior is ok for
  most use cases, dotctl needs the real architecture in order to install native
  packages/libraries/apps.

  Most operating systems do not support multiple architectures during runtime by
  default, and thus the build-time approach of the uname system call makes
  sense. However:

  - Linux has native support for binfmt_misc since kernel 2.1.43 (1997!)
  - Darwin had Rosetta between 2006 and 2012 to transition PowerPC to Intel
  - Darwin has Rosetta 2 since 2020 to transition Intel to ARM64 (Apple Silicon)
  - Windows 10 has a x64 emulation solution for its ARM builds (late 2020)
  - Windows 11 has an ARM64EC ABI that supports mixed x64 and ARM code (2021)

  Just to name a few cases. As such, running a Python binary built for an
  architecture distinct from the current CPU architecture is widely possible on
  2020 and onwards.
  """
  SYSTEM = system()
  # tries calling the OS-specific function if available, falling back to the
  # standard platform.machine
  ARCH = MACHINES.get(SYSTEM, platform.machine)().lower()

  return commonArch.get(ARCH, ARCH)
