class ArchiveParser:
  def __init__(self, file_pointer, close_on_del=False):
    self.file_pointer = file_pointer
    self.close_on_del = close_on_del
  
  def __del__(self):
    if self.close_on_del:
      self.file_pointer.close()

  def extractKey(self):
    """Extract the encryption key from an archive"""
    fp = self.file_pointer
    original_pos = fp.tell()
    fp.seek(0, 0)
    key = fp.read(16) # key is first 16 bytes of file
    # return file pointer to original position
    fp.seek(original_pos, 0)
    return key

  @staticmethod
  def loadFile(path):
    """"Open the file and return an ArchiveParser instance """
    filePointer = open(path, "rb")
    return ArchiveParser(filePointer, True)