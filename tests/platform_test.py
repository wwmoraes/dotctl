import pytest
import platform as builtin
from dotctl import platform


@pytest.mark.unit
def test_system():
  GOT = platform.system()
  WANT = builtin.system().lower()
  assert GOT == WANT


@pytest.mark.unit
def test_node():
  GOT = platform.node()
  WANT = builtin.node()
  assert GOT == WANT


@pytest.mark.unit
def test_hostname():
  GOT = platform.hostname()
  WANT = builtin.node().split(".")[0]
  assert GOT == WANT


@pytest.mark.unit
def test_machine():
  GOT = platform.machine()
  assert isinstance(GOT, str)
  assert len(GOT) > 0


@pytest.mark.unit
def test_machine_darwin():
  SYSTEM = builtin.system().lower()
  if SYSTEM.startswith("darwin"):
    GOT = platform._machine_darwin()
    assert isinstance(GOT, str)
    assert len(GOT) > 0
  else:
    with pytest.raises(RuntimeError):
      platform._machine_darwin()


@pytest.mark.unit
def test_machine_linux():
  SYSTEM = builtin.system().lower()
  if SYSTEM.startswith("linux"):
    GOT = platform._machine_linux()
    assert isinstance(GOT, str)
    assert len(GOT) > 0
  else:
    with pytest.raises(RuntimeError):
      platform._machine_linux()
