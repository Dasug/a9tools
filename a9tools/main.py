import argparse
import binascii
import sys
from os.path import exists, getsize, basename

from .archive_parser import ArchiveParser
from .file_dumper import dump_to_file

__version__ = "0.1"

def doExtraction(endAfter, quiet, inputPath, outputPath):
  parser = ArchiveParser.loadFile(inputPath)
  key = parser.extractKey()  
  if not quiet: print("Found Key: 0x" + str(binascii.hexlify(key).decode('UTF-8')))
  if endAfter == "key":
    if outputPath:
      dump_to_file(outputPath[0], key, quiet)
    return
  
  data = parser.loadRawData()
  if not quiet: print("Decrypting...")
  decrypted = parser.decryptData(key, data)
  if endAfter == "decrypt":
    if outputPath:
      dump_to_file(outputPath[0], decrypted, quiet)
    else:
      dump_to_file(basename(inputPath)+".decrypted", decrypted, quiet)
    return

  if not quiet: print("Unpacking...")
  unpacked = parser.unpackData(decrypted)
  if endAfter == "unpack":
    if outputPath:
      dump_to_file(outputPath[0], unpacked, quiet)
    else:
      dump_to_file(basename(inputPath)+".unpacked", unpacked, quiet)
    return
  
  # todo file extraction

def _cmd_extract_key(cmdl_opts):
  doExtraction("key", cmdl_opts.quiet, cmdl_opts.path, cmdl_opts.output)

def _cmd_unpack(cmdl_opts):
  doExtraction("unpack", cmdl_opts.quiet, cmdl_opts.path, cmdl_opts.output)

def _cmd_decrypt(cmdl_opts):
  doExtraction("decrypt", cmdl_opts.quiet, cmdl_opts.path, cmdl_opts.output)

def _cmd_extract(cmdl_opts):
  doExtraction("extract", cmdl_opts.quiet, cmdl_opts.path, cmdl_opts.output)

def _cmd_not_implemented(cmdl_opts):
  print("error: not implemented!")
  sys.exit(3)

def main():
  cmdl_usage = "%(prog)s [options] action path"
  cmdl_action_explanation = """The following actions are available:
  extract        unpacks an archive and extracts the contained files
  pack           pack a folder into an archive
  modify         unpack, modify and re-pack an archive
  extract-key    just extract the archive encryption key
  decrypt        just decrypt the archive without unpacking it
  unpack         unpack an archive and write the binary content into a file"""
  cmdl_version = __version__
  cmdl_parser = argparse.ArgumentParser(usage=cmdl_usage, epilog=cmdl_action_explanation, formatter_class=argparse.RawDescriptionHelpFormatter)

  cmdl_parser.add_argument("-o", "--output", action="store", dest="output", nargs=1, help="output directory or file")
  cmdl_parser.add_argument("-q", "--quiet", action="store_true", dest="quiet", help="do not show output")
  cmdl_parser.add_argument("-v", "--version", action="version", version=cmdl_version)
  cmdl_parser.add_argument("action", action="store", metavar="action", choices=['unpack', 'extract', 'extract-key', 'decrypt', 'pack', 'modify'], help="action to perform")
  cmdl_parser.add_argument("path", action="store", help="path of file or directory")


  cmdl_opts = cmdl_parser.parse_args()

  action = cmdl_opts.action
  file_path = cmdl_opts.path

  if action in ["extract-key", "unpack", "modify", "decrypt"]:
    if not exists(file_path):
      print("error: no such file or directory!")
      sys.exit(1);
    
    if getsize(file_path) <= 16:
      print("error: invalid archive")
      sys.exit(2)
  elif action == "pack":
    pass # todo: check for valid directory
  
  handlers = {
    "unpack": _cmd_unpack,
    "extract": _cmd_not_implemented,#_cmd_extract,
    "extract-key": _cmd_extract_key,
    "decrypt": _cmd_decrypt,
    "pack": _cmd_not_implemented,
    "modify": _cmd_not_implemented
  }
    
  handlers[action](cmdl_opts);

  sys.exit(0)