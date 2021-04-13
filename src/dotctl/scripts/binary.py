import os
from typing import Callable, Optional, Protocol, TypedDict, Union, overload
from urllib.parse import urlparse
from urllib.error import URLError
import shutil
import requests
import tempfile
import tarfile
import zipfile
import io
import json

from dotctl import AnyPathLike
from dotctl.context import Context, ContextInfo
from dotctl.scripts import messages


def fetch(url: str) -> bytes:
  response = requests.get(url)
  if not response.ok:
    response.raise_for_status()
  elif response.status_code != 200:
    raise requests.models.HTTPError(
      f"expected a 200 OK response, got {response.status_code}"
    )

  return response.content


def tmp_file(content: bytes) -> str:
  fd, src = tempfile.mkstemp()
  os.write(fd, content)
  os.close(fd)
  return src


def install(src: str, dst: str) -> None:
  """replace the destination file with the source, and makes it executable

  changes both the owner user and group to the current process values.
  Also changes the destination file modifiers to 0750.
  """
  os.replace(src, dst)
  os.chown(dst, os.getuid(), os.getgid())
  # sets the binary as accessible only by its owner when installed under the
  # home folder. Otherwise it's set as both readable and executable by everyone,
  # and writable only by the installer user.
  if dst.startswith(os.path.expanduser("~")):
    os.chmod(dst, 0o700)
  else:
    os.chmod(dst, 0o755)  # nosec


class Unarchiver(Protocol):
  """extracts in-memory a file from an archive"""

  def __call__(self, content: bytes, name: str) -> bytes:
    """extracts the `name` file from the `content` archive

    :param content: archive bytes
    :param name: file name and/or path to extract (implementation-dependant)
    :return: file bytes
    """
    ...


class GitReleaseInfo(TypedDict):
  repository: str
  name: str
  version: str
  context: ContextInfo


class PatternFilename(Protocol):
  """pattern file name generator"""

  def __call__(self, info: GitReleaseInfo) -> str:
    """produces a file name based on a base name, version and context data

    :param name: base name of the file (e.g. binary or project name)
    :param version: version number
    :param context: current host information, such as architecture and OS type
    :return: pattern-formatted file name
    """
    ...


class PatternTag(Protocol):
  """pattern tag name generator"""

  def __call__(self, version: str, context: ContextInfo) -> str:
    """produces a tag name based on a version and context data

    :param version: version number
    :param context: current host information, such as architecture and OS type
    :return: pattern-formatted tag name
    """
    ...


def untar(content: bytes, name: str) -> bytes:
  """in-memory file bytes extraction for tar archives"""
  with io.BytesIO(content) as buffer:
    tar = tarfile.open(fileobj=buffer, mode="r")
    filebuffer = tar.extractfile(name)
    if filebuffer is None:
      raise FileNotFoundError(name)
    return filebuffer.read()


def unzip(content: bytes, name: str) -> bytes:
  """in-memory file bytes extraction for zip archives"""
  with io.BytesIO(content) as buffer:
    zip = zipfile.ZipFile(file=buffer, mode="r")
    zip_member = zip.getinfo(name)
    if zip_member.is_dir():
      raise FileNotFoundError(name)
    with zip.open(zip_member, "r") as src:
      return src.read()


class Remote:
  """fetches and installs a remote binary"""

  @overload
  def __init__(
    self,
    target_name: str,
    source_url: str,
    source_name: Optional[str] = None,
    unarchiver: Optional[Unarchiver] = None,
  ) -> None:
    ...

  @overload
  def __init__(
    self,
    target_name: str,
    source_url: PatternFilename,
    source_name: Optional[str] = None,
    unarchiver: Optional[Unarchiver] = None,
  ) -> None:
    ...

  def __init__(
    self,
    target_name: str,
    source_url: Union[str, PatternFilename],
    source_name: Optional[Union[str, PatternFilename]] = None,
    unarchiver: Optional[Unarchiver] = None,
  ) -> None:
    """validates the source URL and prepares for fetching the remote file

    if the remote is an archive, then unarchiver must be set with a functor
    that transforms the fetched bytes into the final file bytes (i.e. extract
    the binary). The `source_name` is passed as a second parameter, and as such
    must comply to any requirements of the archive type (e.g. )

    :param source_url: absolute URL where the file can be fetched from
    :param target_name: binary name to install as and check if installed
    :param source_name: binary name on the source (defaults to the target name)
    :param unarchiver: optional unarchiver to apply to the fetched file
    :raises URLError: source URL is invalid
    """
    context = Context.from_env()
    source_name = source_name or target_name
    if isinstance(source_name, str):
      self.source_name = source_name
    else:
      self.source_name = source_name({
        "repository": "",
        "name": target_name,
        "version": "",
        "context": context,
      })

    if isinstance(source_url, str):
      self.url = source_url
    else:
      self.url = source_url({
        "repository": "",
        "name": self.source_name or target_name,
        "version": "",
        "context": context,
      })

    parsed_url = urlparse(self.url)
    if parsed_url.netloc == "" or parsed_url.scheme == "":
      raise URLError(f"invalid URL {source_url}")
    self.target_name = target_name
    self.unarchiver = unarchiver

  def is_installed(self) -> bool:
    return shutil.which(self.target_name) is not None

  def process(self, content: bytes) -> str:
    if self.unarchiver:
      content = self.unarchiver(content, self.source_name)
    return tmp_file(content)

  def install(self, dst_dir: AnyPathLike) -> None:
    """fetches and installs the binary

    replaces the file at the destination directory
    """

    # check if the directory exists
    if not os.path.isdir(dst_dir):
      raise NotADirectoryError(dst_dir)

    # get the canonical destination directory
    dst_dir = os.path.realpath(dst_dir)

    # warn if the destination directory is not on the OS PATH
    if not dst_dir in os.environ.get("PATH", "").split(":"):
      messages.warning(f"destination directory is not on PATH")

    # fetch file
    content = fetch(self.url)

    # process the content bytes and save into a temporary file
    tmp_path = self.process(content)

    # install the file into the destination
    install(tmp_path, os.path.join(str(dst_dir), self.target_name))


class GitHubRelease(Remote):
  """fetches and install a release binary asset from a Github release"""

  @staticmethod
  def latest_version(repository: str) -> str:
    response = requests.get(
      f"https://api.github.com/repos/{repository}/releases"
    )
    if not response.ok:
      response.raise_for_status()
    data = json.loads(response.content)
    return str(data[0]["tag_name"])

  def __init__(
    self,
    target_name: str,
    repository: str,
    file: Union[str, PatternFilename],
    source_name: Optional[str] = None,
    unarchiver: Optional[Unarchiver] = None,
    version: Optional[str] = None,
    tag: Optional[PatternTag] = None,
    download_base_url: Optional[str] = None,
  ) -> None:
    """creates a Remote fetcher instance for a github binary release

    :param repository: github repository with owner (e.g. owner/repository)
    :param file: functor to generate the target file name
    :param target_name: binary name to install as and check if installed
    :param source_name: binary name on the source (defaults to the target name)
    :param unarchiver: optional unarchiver to apply to the fetched file
    :param version: version to install (defaults to latest)
    :param tag: functor to generate the tag name (defaults to the version)
    :raises URLError: source URL is invalid
    """
    context = Context.from_env()
    base_url = f"https://github.com/{repository}"
    # either use the provided version or get the latest one from the upstream
    target_version = version or self.latest_version(repository)
    # apply the tag functor if provided
    target_tag = tag(target_version, context) if tag else target_version
    # apply the file name functor, if present
    if isinstance(file, str):
      source_file = file
    else:
      source_file = file(
        info={
          "repository": repository,
          "name": source_name or target_name,
          "version": target_version,
          "context": context,
        }
      )
    download_base_url = download_base_url or f"{base_url}/releases/download/{target_tag}"
    source = f"{download_base_url}/{source_file}"
    super().__init__(
      source_url=source,
      target_name=target_name,
      source_name=source_name,
      unarchiver=unarchiver,
    )
