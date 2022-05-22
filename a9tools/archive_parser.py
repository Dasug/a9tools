class ArchiveParser:
  FIXED_KEY = b'\x3b\x16\x6f\xd8\xac\xb2\x09\xfc\xb0\x9d\xa9\x3a\xdc\xa1\x3f\xd2\x45\x17\x11\x03\xfb\x59\x5e\x21\xd3\x7a\x41\xe8\x6a\x34\xd9\x10\x66\x21\xa7\x21\xff\x2e\x37\x89\xbf\x4e\x03\xec\x85\x6b\x94\xbb\xd0\xa2\xea\x08\x3a\xaf\x1e\x99\x43\xa6\x46\x3b\x50\xe5\x99\x58\xf4\x46\xd4\xcc\x6d\x99\xdc\xf5\x72\x51\xa4\x09\x2c\x7d\x51\xad\x82\xfa\x9c\xc3\x99\xe7\x78\x83\x9b\x5a\xf5\xcd\xb8\x51\x65\xbd\x6b\xec\xbd\x81\xff\xd9\x3e\x67\x51\x0f\x54\x3a\xd7\xbf\xbe\xcf\xe1\x87\xef\xdb\x1f\xea\xb4\x07\x64\xfd\x18\x47\xa9\x62\x85\x67\x55\x7a\x2b\xe7\xbc\xd7\xa5\x08\xe5\xf0\xda\x27\x90\x19\x22\x4a\x77\xb2\xab\xf9\xd5\x9e\x1a\x4f\x25\xf7\x75\x50\x2c\xff\x40\x7d\x39\x5a\xe6\xa6\xac\x7b\x5b\x00\xb5\x5d\x00\x77\x5e\x73\xc7\x45\xcc\xe1\x97\xc4\xc1\xec\xf2\x80\x66\xaf\xd5\x91\x48\x10\xdf\x28\xa0\xf3\xb6\x67\xd7\xae\xa7\x76\x49\xbc\x8c\xd3\x4a\xb5\xf3\xe9\x66\x7d\x7c\xe5\xed\xbc\x83\xc5\xb0\x8f\xff\xb1\x05\x7e\xaa\x8f\x11\xad\x63\xd2\x46\x56\xd0\x92\x2a\x76\x47\xe2\x5a\xc7\xef\x5e\xcf\xef\x22\x03\x61\xf7\x16\x44\x89\xfe\xbd\x59\x6b\x2f\xe9\xdb'

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

  def loadRawData(self):
    fp = self.file_pointer
    original_pos = fp.tell()
    fp.seek(16, 0) # data starts 16 bytes after start of the file
    content = fp.read()
    # return file pointer to original position
    fp.seek(original_pos, 0)
    return content

  def decryptData(self, file_key, data):
    length = len(data)
    result = bytearray(length)
    for i in range(length):
      fixed_byte = self.FIXED_KEY[i % 256] # rotate through 256 byte fixed key
      file_byte = file_key[i % 16] # rotate through 16 bit file specific key
      data_byte = data[i]
      result[i] = file_byte ^ ((data_byte + fixed_byte)&0xff)
    return result

  def unpackData(self, decrypted_data):
    dec_data_length = len(decrypted_data)
    # not exactly sure what's up with this but apparently we need this
    header_length = int.from_bytes(decrypted_data[:4], "little")
    # if header length is unreasonably large or too small, we probably don't have a header
    if dec_data_length < header_length and header_length < (dec_data_length * 0x10):
      decrypted_data = decrypted_data[4:] # data starts after header length indicator
      dec_data_length -= 4
    else:
      header_length = 0
    
    # decompression algorithm - mostly reverse engineered, I don't completely understand it
    flags = 0
    r = 0xfee
    inPosition = 0
    text_buf = bytearray(0x1000) # create empty buffer of length 4096
    unpacked_data = bytearray()

    while(inPosition < dec_data_length):
      if (flags & 0x100) == 0:
        inByte = decrypted_data[inPosition]
        inPosition+=1
        flags = int.from_bytes([0xff, inByte], "big")
      if (flags & 1) == 0:
        if (inPosition+1) >= dec_data_length: # end of data reached
          break
        firstByte = decrypted_data[inPosition]
        secondByte = decrypted_data[inPosition+1]
        inPosition+=2
        for k in range(0,(secondByte & 0xf)+3):
          outByte = text_buf[(firstByte | (secondByte & 0xf0) << 4) + k & 0xfff]
          unpacked_data.append(outByte)
          text_buf[r] = outByte
          r = (r+1) & 0xfff
      else:
        if inPosition >= dec_data_length: # end of data reached
          break
        inByte = decrypted_data[inPosition]
        inPosition+=1
        unpacked_data.append(inByte)
        text_buf[r] = inByte
        r = (r+1) & 0xfff;

      flags = flags >> 1
    
    return unpacked_data

  @staticmethod
  def loadFile(path):
    """"Open the file and return an ArchiveParser instance """
    filePointer = open(path, "rb")
    return ArchiveParser(filePointer, True)