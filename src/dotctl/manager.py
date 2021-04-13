import os
import subprocess
import sys
from typing import Callable, Generator, List, Optional, Tuple
from colorama import Fore, Style
import importlib.util
from multiprocessing import Process
import inspect
import shutil
import itertools
from dotctl import AnyPathLike
from dotctl.scripts import messages
from dotctl.context import Context


def run_setup_script(script: str):
  setup = Manager.get_setup_fn(script)
  setup()


class Manager:
  """Installs stow packages and runs setup scripts

  Packages are either global, OS-specific or tag-specific directories containing
  files that will be linked to the target folder. Scripts can read files from
  the repository to retrieve needed data (e.g. applications/packages to install
  from a specific language registry, one-off settings, etc)
  """

  SYSTEMS_DIRNAME = ".systems"
  HOSTS_DIRNAME = ".hostnames"
  SETUPS_DIRNAME = ".setup.d"

  @staticmethod
  def list_packages(dir: AnyPathLike) -> Generator[str, None, None]:
    """lists packages under the given directory

    packages are non-hidden (i.e. do not start with dot) directories
    """

    packages = os.scandir(str(dir))

    for package in packages:
      if not package.is_dir():
        continue

      package_name = str(package.name)
      if package_name.startswith("."):
        continue

      yield package_name

  @staticmethod
  def stow_package(
    dir: AnyPathLike,
    target: AnyPathLike,
    package: str,
  ) -> subprocess.Popen[str]:
    return subprocess.Popen(
      ["stow", "-d", dir, "-t", target, "-R", package],
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      text=True,
    )

  @staticmethod
  def is_setup_fn(script: str, setup: Callable) -> Callable[[], int]:
    if setup is None:
      raise RuntimeError(f"setup function not found on {script}")

    if inspect.iscoroutinefunction(setup):
      raise RuntimeError(
        f"cannot run setup function of {script}: async is not allowed"
      )

    defspec = inspect.getfullargspec(setup)

    if "return" not in defspec.annotations:
      raise RuntimeError(
        f"cannot run setup function of {script}: no return type defined"
      )

    returnspec = defspec.annotations.get("return")
    if returnspec is not None:
      print(f"WARNING setup function of {script} should return None")
    # if not issubclass(returnspec, int):
    #   raise RuntimeError("cannot run setup function: return type is not int")

    argcount = len(defspec.args or []) > 0

    if argcount > 0:
      print(f"WARNING setup function of {script} should not have arguments")

    if argcount != len(defspec.defaults or []):
      raise RuntimeError(
        f"cannot run setup function of {script}: an argument is required"
      )

    if defspec.varargs is not None:
      print(
        f"WARNING setup function of {script} should not expect variable arguments"
      )

    if defspec.varkw is not None:
      print(
        f"WARNING setup function of {script} should not expect keyword arguments"
      )

    kwonlycount = len(defspec.kwonlyargs)

    if kwonlycount > 0:
      print(
        f"WARNING setup function of {script} should not expect keyword-only arguments"
      )

    if kwonlycount != len((defspec.kwonlydefaults or {}).keys()):
      raise RuntimeError(
        f"cannot run setup function of {script}: a keyword-only argument is required"
      )

    return setup

  @classmethod
  def get_setup_fn(cls, script: str) -> Callable[[], int]:
    name = os.path.basename(script).removesuffix(".py")
    spec = importlib.util.spec_from_file_location(name, script)
    if spec is None or spec.loader is None:
      raise RuntimeError(f"unable to load spec of {script}")
    module = spec.loader.load_module(name)
    return cls.is_setup_fn(script, getattr(module, "setup", None))

  def __init__(self, dir: AnyPathLike) -> None:
    """

    returns a new instance if the directory provided exists
    """

    self.context = Context(dir)
    self.dir = str(dir)

    osdir = os.path.join(self.dir, self.SYSTEMS_DIRNAME, self.context.SYSTEM)
    self.osdir = osdir if os.path.isdir(osdir) else None

    hostdir = os.path.join(self.dir, self.HOSTS_DIRNAME, self.context.HOST)
    self.hostdir = hostdir if os.path.isdir(hostdir) else None

    setupdir = os.path.join(self.dir, self.SETUPS_DIRNAME)
    self.setupdir = setupdir if os.path.isdir(setupdir) else None

    if self.context.SYSTEM != "":
      ossetupdir = os.path.join(
        self.dir, self.SETUPS_DIRNAME, self.context.SYSTEM
      )
      self.ossetupdir = ossetupdir if os.path.isdir(ossetupdir) else None
    else:
      self.ossetupdir = None

  def install(self, target: Optional[AnyPathLike] = None) -> None:
    if shutil.which("stow") is None:
      raise RuntimeError("stow is not installed")

    if target is None:
      target = os.path.expanduser("~")

    processes: List[
      Tuple[AnyPathLike, AnyPathLike, str, subprocess.Popen[str]]
    ] = [
      (self.dir, target, package, self.stow_package(self.dir, target, package))
      for package in self.list_packages(self.dir)
    ]

    if self.osdir is not None:
      processes.extend([(
        self.osdir, target, package,
        self.stow_package(self.osdir, target, package)
      ) for package in self.list_packages(self.osdir)])

    if self.hostdir is not None:
      processes.extend([(
        self.hostdir, target, package,
        self.stow_package(self.hostdir, target, package)
      ) for package in self.list_packages(self.hostdir)])

    while processes:
      for (index, (dir, target, package, process)) in enumerate(processes):
        retcode = process.poll()
        if retcode is None:
          continue

        processes.pop(index)

        group = str(dir).removeprefix(self.dir)
        if len(group) == 0:
          group = "global"
        elif group.startswith(f"/{self.SYSTEMS_DIRNAME}/"):
          group = "(OS) " + group.removeprefix(f"/{self.SYSTEMS_DIRNAME}/")
        elif group.startswith(f"/{self.HOSTS_DIRNAME}/"):
          group = "(Host) " + group.removeprefix(f"/{self.HOSTS_DIRNAME}/")

        if retcode != 0:
          print(
            messages.failure(
              f"stow {Fore.LIGHTBLUE_EX}{group}{Style.RESET_ALL} {messages.package(package)}"
            ),
            file=sys.stderr
          )
        else:
          print(
            messages.success(
              f"stow {Fore.LIGHTBLUE_EX}{group}{Style.RESET_ALL} {messages.package(package)}"
            )
          )

        if process.stdout is not None:
          stdout_lines = process.stdout.readlines()
          if len(stdout_lines) > 0:
            print("\n".join(stdout_lines))

        if process.stderr is not None:
          stderr_lines = [
            line for line in process.stderr.readlines()
            if not line.startswith("BUG in find_stowed_path?")
          ]
          if len(stderr_lines) > 0:
            print("\n".join(stderr_lines), file=sys.stderr)

        break

  def setup(self) -> None:
    if self.setupdir is None:
      print("setup directory does not exist", file=sys.stderr)
      sys.exit(1)

    self.context.update_environment()

    scripts = sorted(
      itertools.chain(
        [
          script for script in os.scandir(self.setupdir)
          if script.is_file() and script.name.endswith(".py")
        ],
        [
          script for script in os.scandir(self.ossetupdir)
          if script.is_file() and script.name.endswith(".py")
        ] if self.ossetupdir is not None else [],
      ),
      key=lambda entry: entry.name,
    )
    exit_code = 0
    for script in scripts:
      try:
        process = Process(target=run_setup_script, args=(script.path,))
        process.start()
        process.join()
      except Exception as err:
        print(err, file=sys.stderr)
        exit_code = 1
        continue
    sys.exit(exit_code)
