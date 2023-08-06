"""NEWDES and NEWDES-96 cipher implementations in pure Python.

This implementation is in the public domain. Attribution is not desired.
Since this is implemented in pure Python, it's bound to be mind-boggingly slow.
Sorry about that. :)

For information regarding the algorithm, refer to:
http://www.mirrors.wiretapped.net/security/cryptography/algorithms/newdes/
"""

# cipher properties
key_size = 15
block_size = 8

min_key_size = max_key_size = key_size

# mode constants
MODE_ECB = 1
MODE_CBC = 2


# block-XOR functions for the CBC mode of operation

try:
  # Crypto.Cipher.XOR implementation of block-XOR
  from Crypto.Cipher.XOR import new as new_xor
  def block_xor(a, b):
    """XOR two N-byte strings bit-wise and return the result in another string."""

    return new_xor(a).encrypt(b)

except ImportError:
  # struct-based implementation of block-XOR for fallback
  import struct
  q_struct = struct.Struct("q")
  def block_xor(a, b):
    """XOR two 8-byte strings bit-wise and return the result in another string."""

    q = q_struct
    return q.pack((q.unpack(a)[0])^(q.unpack(b)[0]))

# ----


newdes_rotor = [
   32,137,239,188,102,125,221, 72,212, 68, 81, 37, 86,237,147,149,
   70,229, 17,124,115,207, 33, 20,122,143, 25,215, 51,183,138,142,
  146,211,110,173,  1,228,189, 14,103, 78,162, 36,253,167,116,255,
  158, 45,185, 50, 98,168,250,235, 54,141,195,247,240, 63,148,  2,
  224,169,214,180, 62, 22,117,108, 19,172,161,159,160, 47, 43,171,
  194,175,178, 56,196,112, 23,220, 89, 21,164,130,157,  8, 85,251,
  216, 44, 94,179,226, 38, 90,119, 40,202, 34,206, 35, 69,231,246,
   29,109, 74, 71,176,  6, 60,145, 65, 13, 77,151, 12,127, 95,199,
   57,101,  5,232,150,210,129, 24,181, 10,121,187, 48,193,139,252,
  219, 64, 88,233, 96,128, 80, 53,191,144,218, 11,106,132,155,104,
   91,136, 31, 42,243, 66,126,135, 30, 26, 87,186,182,154,242,123,
   82,166,208, 39,152,190,113,205,114,105,225, 84, 73,163, 99,111,
  204, 61,200,217,170, 15,198, 28,192,254,134,234,222,  7,236,248,
  201, 41,177,156, 92,131, 67,249,245,184,203,  9,241,  0, 27, 46,
  133,174, 75, 18, 93,209,100,120, 76,213, 16, 83,  4,107,140, 52,
   58, 55,  3,244, 97,197,238,227,118, 49, 79,230,223,165,153, 59
  ]

class newdes(object):
  """The original NEWDES cipher, as published in Cryptologia in January 1985."""

  def __init__(self, key, mode=None, IV=None):
    self.setkey(key)

    if mode is None:
      # derive mode from the IV argument
      if IV is None:
        mode = MODE_ECB
      else:
        mode = MODE_CBC

    self.mode = mode
    if mode == MODE_CBC:
      self.iv = IV

  # generic routines
  def encrypt(self, buffer):
    if self.mode == MODE_ECB:
      return self.encrypt_ecb(buffer)
    else:
      return self.encrypt_cbc(buffer)

  def decrypt(self, buffer):
    if self.mode == MODE_ECB:
      return self.decrypt_ecb(buffer)
    else:
      return self.decrypt_cbc(buffer)

  # ECB mode routines
  def encrypt_ecb(self, buffer):
    result = ''
    for offset in range(0, len(buffer), 8):
      result += self.newdes_block(self.enckey_unravelled, buffer[offset:offset+8])
    return result

  def decrypt_ecb(self, buffer):
    result = ''
    for offset in range(0, len(buffer), 8):
      result += self.newdes_block(self.deckey_unravelled, buffer[offset:offset+8])
    return result

  # CBC mode routines
  def encrypt_cbc(self, buffer):
    iv = self.iv

    result = ''
    for offset in range(0, len(buffer), 8):
      plaintext = buffer[offset:offset+8]
      block = block_xor(plaintext, iv)

      ciphertext = self.newdes_block(self.enckey_unravelled, block)
      result += ciphertext
      iv = ciphertext

    self.iv = iv
    return result

  def decrypt_cbc(self, buffer):
    iv = self.iv

    result = ''
    for offset in range(0, len(buffer), 8):
      ciphertext = buffer[offset:offset+8]
      plaintext = self.newdes_block(self.deckey_unravelled, ciphertext)

      result += block_xor(plaintext, iv)
      iv = ciphertext

    self.iv = iv
    return result

  # cipher implementation methods
  def setkey(self, key):
    key = map(ord, key)
    self.enckey_unravelled = key * 4

    self.deckey_unravelled = deckey = []
    keyidx = 11
    while True:
      deckey.append(key[keyidx])
      keyidx = (keyidx + 1) % key_size

      deckey.append(key[keyidx])
      keyidx = (keyidx + 1) % key_size

      deckey.append(key[keyidx])
      keyidx = (keyidx + 1) % key_size

      deckey.append(key[keyidx])
      keyidx = (keyidx + 9) % key_size

      if keyidx == 12:
        break

      deckey.append(key[keyidx])
      keyidx += 1
      deckey.append(key[keyidx])
      keyidx += 1

      deckey.append(key[keyidx])
      keyidx = (keyidx + 9) % 15

  def newdes_block(self, key, block):
    b0, b1, b2, b3, b4, b5, b6, b7 = map(ord, block)

    rotor = newdes_rotor
    for i in (0, 7, 14, 21, 28, 35, 42, 49):
      b4 ^= rotor[b0 ^ key[i  ]]
      b5 ^= rotor[b1 ^ key[i+1]]
      b6 ^= rotor[b2 ^ key[i+2]]
      b7 ^= rotor[b3 ^ key[i+3]]

      b1 ^= rotor[b4 ^ key[i+4]]
      b2 ^= rotor[b4 ^ b5]
      b3 ^= rotor[b6 ^ key[i+5]]
      b0 ^= rotor[b7 ^ key[i+6]]

    b4 ^= rotor[b0 ^ key[56]]
    b5 ^= rotor[b1 ^ key[57]]
    b6 ^= rotor[b2 ^ key[58]]
    b7 ^= rotor[b3 ^ key[59]]

    result = (b0, b1, b2, b3, b4, b5, b6, b7)
    return ''.join(map(chr, result))

class newdes96(newdes):
  """NEWDES-96 is the revised variation of NEWDES with an improved key schedule."""

  def decrypt_cbc(self, buffer):
    iv = self.iv

    result = ''
    for offset in range(0, len(buffer), 8):
      ciphertext = buffer[offset:offset+8]
      plaintext = self.newdes96_decrypt(self.enckey_unravelled, ciphertext)

      result += block_xor(plaintext, iv)
      iv = ciphertext

    self.iv = iv
    return result

  def decrypt_ecb(self, buffer):
    # this decrypt routine uses the same unravelled key
    result = ''
    for offset in range(0, len(buffer), 8):
      result += self.newdes96_decrypt(self.enckey_unravelled, buffer[offset:offset+8])
    return result

  # cipher implementation methods

  # The encryption routine is the same in both NEWDES and NEWDES-96; only the
  # unravelled key differs.
  def setkey(self, key):
    key = map(ord, key) # converts key string into a list of integers
    kk = []             # unravelled key

    for i in xrange(15):
      kk.append(key[i])
      kk.append(key[i] ^ key[7])
      kk.append(key[i] ^ key[8])
      kk.append(key[i] ^ key[9])

    self.enckey_unravelled = kk

  # I don't know how to construct the inverse key (like the old NEWDES
  # implementation does in setkey()) so I'll have to reimplement the decrypt
  # routine.
  def newdes96_decrypt(self, key, block):
    b0, b1, b2, b3, b4, b5, b6, b7 = map(ord, block)

    rotor = newdes_rotor
    for i in (59, 52, 45, 38, 31, 24, 17, 10):
      b7 ^= rotor[b3 ^ key[i  ]]
      b6 ^= rotor[b2 ^ key[i-1]]
      b5 ^= rotor[b1 ^ key[i-2]]
      b4 ^= rotor[b0 ^ key[i-3]]

      b0 ^= rotor[b7 ^ key[i-4]]
      b3 ^= rotor[b6 ^ key[i-5]]
      b2 ^= rotor[b4 ^ b5]
      b1 ^= rotor[b4 ^ key[i-6]]

    b7 ^= rotor[b3 ^ key[3]]
    b6 ^= rotor[b2 ^ key[2]]
    b5 ^= rotor[b1 ^ key[1]]
    b4 ^= rotor[b0 ^ key[0]]

    result = (b0, b1, b2, b3, b4, b5, b6, b7)
    return ''.join(map(chr, result))

# for Python cipher API compatibility; defaults to NEWDES-96
new = newdes96

