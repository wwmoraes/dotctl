import json
import os
from typing import Generator


class Packages:
  """Package list generator

  produces an interator that consumes the global, system and tag-based source
  files package entries
  """

  def __init__(self, basepath: os.PathLike, filename: str):
    """checks the global, system and tag-based source files

    Package source files paths:
    - <basepath>/packages/<filename>
    - <basepath>/packages/<SYSTEM>/<filename>
    - <basepath>/packages/<TAG>/<filename>

    Missing files are ignored.
    """
    SYSTEM = os.environ["SYSTEM"]
    TAGS = os.environ.get("TAGS", "")
    self.sources = [
      source for source in [
        os.path.join(basepath, "packages", filename),
        os.path.
        join(basepath, "packages", SYSTEM, filename) if SYSTEM else None, *[
          os.path.join(basepath, "packages", tag, filename)
          for tag in TAGS.split(",")
          if tag
        ]
      ] if source and os.path.isfile(source)
    ]

  def __iter__(self) -> Generator[str, None, None]:
    for source in self.sources:
      if not os.path.isfile(source):
        print(f"{source} not found")
        continue
      yield from (
        line.strip("\n")
        for line in open(source, "r")
        if not line.startswith("#")
      )
