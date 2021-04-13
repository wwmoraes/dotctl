import os
from typing import Dict, List, Optional
from dotctl import platform
from dotctl.context import Context, ContextInfo
import pytest
from pathlib import Path
import json


@pytest.mark.unit
@pytest.mark.parametrize(
  "env,tags", [
    ({}, None),
    ({}, ""),
    ({}, "qux"),
    ({
      "ARCH": "supercpu"
    }, None),
    ({
      "SYSTEM": "superos"
    }, None),
    ({
      "ARCH": "supercpu",
      "SYSTEM": "superos"
    }, None),
    ({
      "ARCH": "supercpu",
      "SYSTEM": "superos"
    }, "foo,bar"),
  ]
)
def test_init_with_env(
  tmp_path: Path,
  env: Dict[str, str],
  tags: Optional[str],
):
  os.environ.update(env)
  # creates the tags file if needed
  tmp_tagsrc = os.path.join(tmp_path, ".tagsrc")
  os.environ["TAGSRC"] = tmp_tagsrc
  if tags is not None:
    print("\n".join(tags.split(",")), file=open(tmp_tagsrc, "w"))
  context = Context(tmp_path)
  assert context.DOTFILES_PATH == str(tmp_path)
  assert context.SETUP_PATH == os.path.join(tmp_path, ".setup.d")
  assert context.PACKAGES_PATH == os.path.join(tmp_path, ".setup.d", "packages")
  assert context.ARCH == env.get("ARCH", platform.machine())
  assert context.SYSTEM == env.get("SYSTEM", platform.system())
  assert context.HOST == platform.hostname()
  assert context.TAGS == (tags or "")


@pytest.mark.unit
def test_init_invalid_dir(tmp_path):
  with pytest.raises(RuntimeError):
    Context(os.path.join(tmp_path, "test"))


@pytest.mark.unit
@pytest.mark.parametrize(
  "env", [
    {},
    {
      "ARCH": "supercpu"
    },
    {
      "DOTFILES_PATH": "test/dotfiles",
    },
    {
      "HOST": "test.local",
    },
    {
      "PACKAGES_PATH": "test/dotfiles/.setup.d/packages",
    },
    {
      "SETUP_PATH": "test/dotfiles/.setup.d",
    },
    {
      "SYSTEM": "superos",
    },
    {
      "TAGS": "['qux']",
    },
    {
      "TAGS": "['foo', 'bar']",
    },
    {
      "ARCH": "supercpu",
      "DOTFILES_PATH": "test/dotfiles",
      "HOST": "test.local",
      "PACKAGES_PATH": "test/dotfiles/.setup.d/packages",
      "SETUP_PATH": "test/dotfiles/.setup.d",
      "SYSTEM": "superos",
      "TAGS": "['test']",
    },
  ]
)
def test_from_env(env: Dict[str, str]):
  # cleanup the environment, as we set some safe defaults on conftest
  [os.environ.pop(key, None) for key in ContextInfo.__annotations__.keys()]
  os.environ.update(env)
  info = Context.from_env()
  # tests all defined keys
  for key in ContextInfo.__annotations__.keys():
    assert info.get(key, "") == env.get(key, ""), f"{key} does not match"


@pytest.mark.unit
def test_update_env(tmp_path: Path):
  context = Context(tmp_path)
  context.update_environment()
  for key in [
    "ARCH", "DOTFILES_PATH", "HOST", "PACKAGES_PATH", "SETUP_PATH", "SYSTEM"
  ]:
    assert os.environ.get(key) == getattr(context, key)
  os.environ.get("TAGS") == context.TAGS
