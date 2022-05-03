import argparse
import sys

__version__ = "0.1"


def main():
  cmdl_usage = "%(prog)s [options] action path"
  cmdl_action_explanation = """The following actions are available:
  unpack         unpack an archive
  extract-key    extract the encryption key and print it as a hexadecimal string
  pack           pack a folder into an archive
  modify         unpack, modify and re-pack an archive"""
  cmdl_version = __version__
  cmdl_parser = argparse.ArgumentParser(usage=cmdl_usage, epilog=cmdl_action_explanation, formatter_class=argparse.RawDescriptionHelpFormatter)

  cmdl_parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="do not show output")
  cmdl_parser.add_argument("-v", "--version", action="version", version=cmdl_version)
  cmdl_parser.add_argument("action", action="store", metavar="action", choices=['unpack', 'extract-key', 'pack', 'patch'], help="action to perform")
  cmdl_parser.add_argument("path", action="store", help="path of file or directory")


  cmdl_opts = cmdl_parser.parse_args()

  action = cmdl_opts.action
  print(action);

  sys.exit(0)