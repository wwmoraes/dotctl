from typing import Union
from os import PathLike

__version__ = "0.0.1"

AnyPathLike = Union[str, bytes, PathLike[str], PathLike[bytes]]
