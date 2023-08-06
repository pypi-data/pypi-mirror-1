"""Various utility functions used in OpenKremlin"""

import struct   # for readstruct()
import math     # for format_bytes()
import os.path  # for sanitize_path()

class GuiError(StandardError):
  """GUI error; used in tkgui to signal an error spawning GUI dialogs."""
  pass


def readstruct(file, fmt):
  size = struct.calcsize(fmt)
  data = file.read(size)
  if len(data) == size:
    return struct.unpack(fmt, data)
  else:
    raise EOFError

def round_up_block(n, mod):
  """If n is not divisible by mod, round n up to the next value that is."""

  return ((n+mod-1)//mod)*mod

def round_down_block(n, mod):
  """If n is not divisible by mod, round n down to the value that is."""

  return (n//mod)*mod

def sanitize_path(path):
  """Elaborate path sanitization; input paths use Windows path semantics;
  output uses the current operating system's native path convention and is
  always a relative path."""

  # Windows follows forward slashes as well; canonicalize all to forward slashes
  path = path.replace('\\', '/')
  # strip all trailing slashes (legitimate in case it denotes a directory)
  path = path.rstrip('/')

  if path.startswith('/'):
    path = path.lstrip('/')
    abspath = True
  elif len(path) > 1 and path[1] == ':':
    path = path[2:]
    abspath = True
  else:
    abspath = False

  if ':' in path:
    # separate "file forks" are denoted by the ':' symbol; we'll just ignore
    # everything after this symbol
    path = path.split(':', 1)[0]

  if abspath and '/' in path:
    path = path.rsplit('/', 1)[1]

  # check each path component
  parts = []
  for part in path.split('/'):
    if part.strip('.') == '':
      # path contains just '.' symbols which go backwards in the directory
      # hierarchy; these are completely illegitimate anyway, so we make no
      # attempts to parse them
      continue

    if part.startswith('$'):
      # Windows uses the '$' prefix to denote some "magical" paths; prefix that
      # with '_' just in case
      part = '_' + part

    parts.append(part)

  if len(parts) == 0:
    # unsalvageably incoherent path
    return None

  # join parts according to the running system's path semantics
  path = os.path.join(*parts)

  return path

def format_bytes(bytes):
  """Format a byte count into the optimal representation (kB, MB, etc) while
  keeping at least three digits visible at all times.

  >>> util.format_bytes(12345678)
  '11.8M'
  >>> util.format_bytes(1024*1023)
  '1023k'
  """

  if bytes == 0:
    exp = 0     # math.log(0) is an error
  else:
    exp = int(math.log(bytes, 1024))

  suffix = 'bkMGTPEZY'[exp]
  if exp == 0:
    return '%d%s' % (bytes, suffix)

  converted = float(bytes) / float(1024**exp)
  magnitude = int(math.log(converted, 10))
  return '%.*f%s' % (2-magnitude, converted, suffix)

def fix_checksum(crc):
  """Fixes the result from zlib.adler32() on 64-bit platforms; see
  http://bugs.python.org/issue1202 """

  # specify as long to avoid getting a negative int result with Python 2.3 and earlier
  if crc >= 0x80000000L:
    return crc - ((crc & 0x80000000L) <<1)
  else:
    return crc

