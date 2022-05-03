import argparse
import binascii
import sys
from os.path import exists, getsize

from .archive_parser import ArchiveParser

__version__ = "0.1"

def _cmd_extract_key(cmdl_opts):
  parser = ArchiveParser.loadFile(cmdl_opts.path)
  key = parser.extractKey()
  print("Key: 0x" + str(binascii.hexlify(key).decode('UTF-8')))

def _cmd_not_implemented(cmdl_opts):
  print("error: not implemented!")
  sys.exit(3)

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
  cmdl_parser.add_argument("action", action="store", metavar="action", choices=['unpack', 'extract-key', 'pack', 'modify'], help="action to perform")
  cmdl_parser.add_argument("path", action="store", help="path of file or directory")


  cmdl_opts = cmdl_parser.parse_args()

  action = cmdl_opts.action
  file_path = cmdl_opts.path

  if action in ["extract-key", "unpack", "modify"]:
    if not exists(file_path):
      print("error: no such file or directory!")
      sys.exit(1);
    
    if getsize(file_path) <= 16:
      print("error: invalid archive")
      sys.exit(2)
  elif action == "pack":
    pass # todo: check for valid directory
  
  handlers = {
    "unpack": _cmd_not_implemented,
    "extract-key": _cmd_extract_key,
    "pack": _cmd_not_implemented,
    "modify": _cmd_not_implemented
  }
    
  handlers[action](cmdl_opts);

  sys.exit(0)