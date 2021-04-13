from dotctl.installers.homebrew import \
  Formula as HomebrewFormula, \
  Cask as HomebrewCask, \
  Tap as HomebrewTap
from dotctl.installers.node import Yarn
from dotctl.installers.macappstore import MacAppStore
from dotctl.installers.golang import GoMod
from dotctl.installers.python import Python3Pip
from dotctl.installers.vscode import VSCodeExtension
from dotctl.installers.helm import HelmPlugin
from dotctl.installers.krew import Krew
from dotctl.installers.rust import \
  Cargo, Rustup

__all__ = [
  installer.__name__ for installer in [
    Cargo,
    GoMod,
    HelmPlugin,
    HomebrewCask,
    HomebrewFormula,
    HomebrewTap,
    Krew,
    MacAppStore,
    Python3Pip,
    Rustup,
    VSCodeExtension,
    Yarn,
  ]
]
