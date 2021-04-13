from colorama import Fore, Style


def script(title: str) -> str:
  return f"{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}{title}{Style.RESET_ALL}"


def group(title: str) -> str:
  return f"{Style.BRIGHT}{Fore.LIGHTBLUE_EX}{title}{Style.RESET_ALL}"


def package(name: str) -> str:
  return f"{Fore.CYAN}{name}{Style.RESET_ALL}"


def path(name: str) -> str:
  return f"{Fore.BLUE}{name}{Style.RESET_ALL}"


def bin(name: str) -> str:
  return f"{Fore.RED}{name}{Style.RESET_ALL}"


def info(title: str) -> str:
  return f"{Style.BRIGHT}{Fore.LIGHTBLUE_EX}{title}{Style.RESET_ALL}"


def warning(message: str) -> str:
  return f"{Style.BRIGHT}{Fore.YELLOW}WARNING{Style.RESET_ALL} {message}"


def failure(message: str) -> str:
  return f"{Style.BRIGHT}{Fore.RED}FAILURE{Style.RESET_ALL} {message}"


def success(message: str) -> str:
  return f"{Style.BRIGHT}{Fore.GREEN}SUCCESS{Style.RESET_ALL} {message}"
