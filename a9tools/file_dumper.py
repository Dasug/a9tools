import sys

def dump_to_file(path, content, quiet=False):
  try:
    fp = open(path, "wb")
  except FileNotFoundError:
    print(f"File {path} not found.  Aborting")
    sys.exit(1)
  except OSError:
    print(f"OS error occurred trying to open {path}")
    sys.exit(1)
  except Exception as err:
    print(f"Unexpected error opening {path} is",repr(err))
    sys.exit(1)
  else:
    with fp:
      fp.write(content)
      fp.close()  