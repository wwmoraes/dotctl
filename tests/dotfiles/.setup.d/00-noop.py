from dotctl.scripts import dotsetup


@dotsetup(name="no-op")
def setup() -> None:
  print("NOOP!")


if __name__ == "__main__":
  setup()
