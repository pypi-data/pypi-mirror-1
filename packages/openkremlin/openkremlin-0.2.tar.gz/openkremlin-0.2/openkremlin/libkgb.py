"""A library for accessing and decrypting KGB (Kremlin Encrypt) files.

This is the core of OpenKremlin.
"""

from __future__ import generators       # support for the 'yield' statement

import zlib
from kremsha1 import kremsha1
from util import *

kgb_header_length = 128
kgb_header_struct = '<4B 2x B H 2x 4s5s3s'
kgb_passphrase_struct = '8s 20s'

BUFSIZE = 256*1024

# version tag
KGB_VER_30 = 14
KGB_VER_22 = 12
KGB_VER_21 = 11
KGB_VER_20 = 10

# algorithm identifiers
KGB_CIPHER_BLOWFISH = 1
KGB_CIPHER_DES      = 2
KGB_CIPHER_NEWDES   = 4
KGB_CIPHER_SAFER    = 5
KGB_CIPHER_RC4_OLD  = 6
KGB_CIPHER_CAST     = 7
KGB_CIPHER_RC4      = 9

# modes of operation
KGB_MODE_ECB = 0
KGB_MODE_CBC = 1

# exceptions

class KgbError(Exception):
  """Generic errors related to libkgb."""
  pass

class KgbCorruptionError(KgbError):
  """Error raised when the archive is considered corrupt.

  Please note that simply truncated archives will (in most cases) raise the
  EOFError instead."""

  pass


# main implementation

class KgbContext(object):
  """Stores the global details from the archive's header, and contains related
  methods. Intended for internal use within libkgb."""

  def __init__(self, header):
    self.version = header[0]
    self.cipher = header[1]     # cipher identifier
    self.mode = header[2]       # encryption mode (0=ECB, 1=CBC)
    self.index = header[3]      # index present?

    self.header = header
    self.init_cipher()

  def init_cipher(self):
    """Initialize self.cipher_module and other cipher details."""
    self.streamcipher = False
    # kremlin never uses keys over 20 bytes (160 bits)
    self.max_key_size = 20

    if self.cipher == KGB_CIPHER_BLOWFISH:
      from Crypto.Cipher import Blowfish
      self.cipher_module = Blowfish
    elif self.cipher == KGB_CIPHER_CAST:
      from Crypto.Cipher import CAST
      self.cipher_module = CAST
      self.max_key_size = 16
    elif self.cipher == KGB_CIPHER_RC4:
      from Crypto.Cipher import ARC4
      self.cipher_module = ARC4
      self.streamcipher = True
    elif self.cipher == KGB_CIPHER_NEWDES:
      print "NOTE: Using slow pure-Python implementation of NewDES. This will take a while"
      import newdes
      self.cipher_module = newdes
      self.max_key_size = newdes.max_key_size
    elif self.cipher == KGB_CIPHER_RC4_OLD:
      raise NotImplementedError, '"Old" RC4 cipher is not implemented'
    elif self.cipher == KGB_CIPHER_SAFER:
      raise NotImplementedError, "SAFER-SK cipher is not implemented"
    else:
      raise NotImplementedError, "Cipher %d is not recognized" % self.cipher

  def get_cipher(self, key, iv=None):
    """Return the appropriate cipher instance depending on the archive's
    header. Sort of a factory function for ciphers."""
    key = key[:self.max_key_size]

    if self.streamcipher:
      assert iv is None
      return self.cipher_module.new(key)

    if self.mode == KGB_MODE_ECB or iv is None:
      #print 'get_cipher(): ECB, key=%s' % key.encode('hex')
      return self.cipher_module.new(key, self.cipher_module.MODE_ECB)
    elif self.mode == KGB_MODE_CBC:
      #print 'get_cipher(): CBC, key=%s, iv=%s' % (key.encode('hex'), iv.encode('hex'))
      return self.cipher_module.new(key, self.cipher_module.MODE_CBC, iv)
    else:
      raise NotImplementedError, 'Cipher mode %d not implemented' % self.mode

  def get_block_size(self):
    return self.cipher_module.block_size


class KgbEnvelope(object):
  """Represents a KGB encrypted envelope. Intended for internal use within
  libkgb."""

  def __init__(self, context, file, key):
    self.context = context
    self.file = file
    self.parse_envelope(key)

  def parse_envelope(self, key):
    """Reads the envelope header and sets self.cipherkey."""
    local_salt = self.file.read(8)
    if len(local_salt) == 0:
      # already at the end of file, no envelope exists
      # FIXME: is there a cleaner way than raising StopIteration here?
      raise StopIteration
    elif len(local_salt) < 8:
      raise EOFError

    self.cipherkey = kremsha1(key + local_salt).digest()

    self.block_size = self.context.get_block_size()
    self.cipher_header = self.context.get_cipher(self.cipherkey)

    if self.context.mode:
      iv = self.file.read(8)
      if len(iv) < 8:
        raise EOFError
      self.cipher_content = self.context.get_cipher(self.cipherkey, iv)
    else:
      # use the same cipher for headers and content
      self.cipher_content = self.cipher_header

  def read(self, length):
    """Read and decrypt a value 'length' bytes long. length is always padded up
    to the cipher's block size. This function is for reading individual fields
    in file/chunk headers, which never use CBC and don't respect the IV."""

    padded_len = round_up_block(length, self.block_size)
    data = self.file.read(padded_len)
    if len(data) != padded_len:
      raise EOFError

    data = self.cipher_header.decrypt(data)
    #print 'read(%d): %s' % (length, data.encode('hex'))

    return data[:length]

  def skip(self, length):
    padded_len = round_up_block(length, self.block_size)
    start = self.file.tell()
    self.file.seek(padded_len, 1)

    if self.file.tell() - start != padded_len:
      raise EOFError

  def read_content(self, length):
    """Read and decrypt a value 'length' bytes long. This is similar to the
    read() call above, but honors the IV when used with CBC.  length must be a
    multiple of context.block_size, except for the last block in an envelope.

    If the input file is truncated, the function will return as much data as is
    available. This makes it possible to continuously "stream" files which are
    still being downloaded."""

    padded_len = round_up_block(length, self.block_size)
    data = self.file.read(padded_len)

    if len(data) < padded_len:
      # truncated read
      length = round_down_block(len(data), self.block_size)
      # seek back to preserve block-alignment
      self.file.seek(length - len(data), 1)
      return self.cipher_content.decrypt(data[:length])

    elif padded_len == length or self.context.mode == KGB_MODE_ECB:
      # normal read (the IV hack below is skipped in ECB mode)
      data = self.cipher_content.decrypt(data)

    else:
      # Kremlin Encrypt does this weird IV trick on un-aligned final blocks
      new_iv = self.cipher_header.decrypt(data[-8:])
      data = self.cipher_content.decrypt(data)

      self.cipher_content = self.context.get_cipher(self.cipherkey, new_iv)

    return data[:length]

  def read_int(self):
    """Read a 32-bit integer from the envelope"""

    return readstruct(self, '<I')[0]


class KgbEntry(object):
  """A file entry within a KGB archive. Returned from KgbArchive.iter_entries()"""

  def __init__(self, context):
    self.context = context
    self.at_end = False

    # file data envelope. this will be changed by KgbArchive
    self.envelope = None

  def read_entry(self, envelope):
    """Reads and stores metadata for the file entry.

    Throws StopIteration if this is the last entry in an index."""
    filename_len = envelope.read_int()
    if filename_len == 0:
      if self.context.index:
        # A literal file of length 0 terminates the index envelope.
        raise StopIteration
      else:
        raise KgbCorruptionError, "Zero-length filename"

    if filename_len > 4096:
      # This limitation is also enforced by Kremlin Encrypt
      raise KgbCorruptionError, "Filename too long (%d)" % filename_len

    self.filename = envelope.read(filename_len)
    self.filesize  = readstruct(envelope, '<Q')[0]
    self.atime = envelope.read_int()
    self.mtime = envelope.read_int()
    self.attrs = envelope.read_int()

    header_extra = envelope.read_int()
    self.file_extra = envelope.read_int()

    if header_extra > 4096:
      # sanity limit
      raise KgbCorruptionError, "Header extension too long (%d)" % header_extra

    if header_extra > 0:
      # we just ignore the contents of header_extra for now
      envelope.read(header_extra)

  def decrypt_content_old(self, outfile, progress_cb):
    length = remaining = self.filesize

    while remaining > 0:
      # notify progress callback
      progress_cb(length-remaining, length)

      data = self.envelope.read(min(BUFSIZE, remaining))
      if len(data) == 0:
        raise EOFError
      remaining -= len(data)
      outfile.write(data)

    assert remaining == 0
    progress_cb(length, length)

  def skip_old(self):
    self.envelope.skip(self.filesize)

  def decrypt_content_new(self, outfile, progress_cb):
    length = remaining = self.filesize

    while remaining > 0:
      # notify progress callback
      progress_cb(length-remaining, length)

      remaining -= self.decrypt_chunk(outfile)

    assert remaining == 0
    progress_cb(length, length)

  def skip_new(self):
    remaining = self.filesize
    while remaining > 0:
      compressed, plain_size, raw_size = self.read_chunk_header()
      self.envelope.read_content(raw_size)
      data_crc = self.envelope.read_int()
      remaining -= plain_size

  def read_chunk_header(self):
    envelope = self.envelope

    compressed = envelope.read_int()
    if compressed not in (0, 1):
      raise KgbCorruptionError, "Illegal value for boolean: %d" % compressed

    plain_size = envelope.read_int()

    if compressed:
      raw_size = envelope.read_int()
    else:
      raw_size = plain_size

    return (compressed, plain_size, raw_size)

  def decrypt_chunk(self, outfile):
    compressed, plain_size, raw_size = self.read_chunk_header()

    if compressed:
      decomp = zlib.decompressobj()

    remaining = raw_size
    data_crc = 1

    while remaining > 0:
      data = self.envelope.read_content(min(BUFSIZE, remaining))

      if len(data) == 0:
        raise EOFError
      remaining -= len(data)

      data_crc = zlib.adler32(data, data_crc)
      if compressed:
        data = decomp.decompress(data)
      outfile.write(data)

    assert remaining == 0
    if compressed:
      outfile.write(decomp.flush())
      assert len(decomp.unused_data) == 0
      assert len(decomp.unconsumed_tail) == 0

    verify_crc = readstruct(self.envelope, '<i')[0]
    data_crc = fix_checksum(data_crc)

    if verify_crc != data_crc:
      raise KgbCorruptionError, "Data chunk checksum does not match"
    return plain_size

  def decrypt(self, outfile, progress_cb=None):
    """Decrypt a file entry. Data is written into the file-like object in
    argument 'outfile'."""

    assert self.envelope
    assert BUFSIZE % self.envelope.block_size == 0
    assert not self.at_end

    if not progress_cb:
      progress_cb = lambda x, y: None

    if self.context.version < KGB_VER_21:
      self.decrypt_content_old(outfile, progress_cb)
    else:
      self.decrypt_content_new(outfile, progress_cb)

    self.at_end = True

  def skip(self):
    if self.context.version < KGB_VER_21:
      self.skip_old()
    else:
      self.skip_new()

    self.at_end = True


class KgbArchive(object):
  """Handles .kgb archive compression and decompression."""

  def __init__(self, file):
    self.file = file
    self.key = None
    self.contents = None

    try:
      self.read_header()
    except EOFError:
      raise KgbCorruptionError, "Archive too short"

  def read_header(self):
    header = readstruct(self.file, kgb_header_struct)

    if header[8] != 'KRM':
      raise KgbCorruptionError, "Header info does not match; is this a proper .kgb file?"
    self.context = KgbContext(header)

    self.file.seek(kgb_header_length)
    self.salt, self.hash = readstruct(self.file, kgb_passphrase_struct)

  def set_passphrase(self, key):
    """Set the decryption passphrase. Returns True on success or False on
    incorrect passphrase."""

    self.key = key

    testhash = self.hash_passphrase(self.salt, key)
    if testhash == self.hash:
      return True
    else:
      return False

  def hash_passphrase(self, salt, key):
    """Calculate Kremlin Encrypt's passphrase verification hash."""
    cipherkey = kremsha1(key).digest()
    cipher = self.context.get_cipher(cipherkey)

    for i in xrange(1000):
      salt = cipher.encrypt(salt)

    return kremsha1(salt + key).digest()

  def make_envelope(self):
    """Construct a new KgbEnvelope at the current file offset."""
    return KgbEnvelope(self.context, self.file, self.key)

  def read_index(self):
    """Read the file index (list of files) from the archive header and fill
    self.contents. Note that most archives do not contain an index (depending
    on the context.index value)."""

    # the index has its own separate envelope
    envelope = self.make_envelope()
    self.contents = []

    while True:
      try:
        entry = KgbEntry(self.context)
        entry.read_entry(envelope)

        self.contents.append(entry)
      except StopIteration:
        break

  def iter_entries(self):
    """A generator yielding KgbEntry objects."""

    if self.context.index:
      # indexed archive: all file entries are stored in a separate envelope
      # after the file's header
      if self.contents is None:
        self.read_index()

      # FIXME: implement file_extra handling
      for entry in self.contents:
        entry.envelope = self.make_envelope()

        yield entry
        if not entry.at_end:
          entry.skip()

      return

    else:
      # non-indexed archive: file metadata is stored in the same envelope as
      # the file
      while True:
        # make_envelope() currently raises StopIteration so we don't have to
        # handle that here
        envelope = self.make_envelope()

        entry = KgbEntry(self.context)
        entry.read_entry(envelope)
        entry.envelope = envelope

        yield entry
        if not entry.at_end:
          entry.skip()

