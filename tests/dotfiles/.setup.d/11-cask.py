import os

from dotctl.installers import HomebrewCask
from dotctl.scripts import Packages, dotsetup, messages


@dotsetup(name="Brew cask packages")
def setup() -> None:
  installer = HomebrewCask()
  packages = Packages(os.environ.get("SETUP_PATH"), "cask.txt")
  for package in packages:
    name, bin, *_ = package.split(":", 2) + [None]
    print(f"checking {messages.package(name)}...")
    if installer.is_installed(name, os.path.expanduser(bin or "")):
      continue
    print(f"installing {messages.package(name)}...")
    installer.install(name)


if __name__ == "__main__":
  setup()
