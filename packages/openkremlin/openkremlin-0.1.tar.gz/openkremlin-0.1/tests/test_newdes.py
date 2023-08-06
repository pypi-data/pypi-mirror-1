#!/usr/bin/env python

import unittest
import copy
from binascii import hexlify, unhexlify

#### FIXME: this is a hack to get relative imports working
import os, sys
pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(os.path.join(pathname, '..'))
sys.path.append(fullpath)
####

from openkremlin import newdes


class GenericTests(unittest.TestCase):
  def cipher_encdec(self, cipher, plaintext, ciphertext):
    """Verifies simple encryption and decryption, according to specified
    plaintexts and ciphertexts"""

    enc = cipher
    dec = copy.deepcopy(cipher)   # copy the cipher instance for later decryption

    result = enc.encrypt(plaintext)
    self.failUnlessEqual(result, ciphertext)
    result = dec.decrypt(result)
    self.failUnlessEqual(result, plaintext)

  def cipher_split(self, cipher, method):
    """Verifies that the cipher mode produces consistent results when input is
    split into multiple chunks"""
    c1 = cipher
    c2 = copy.deepcopy(cipher)
    input = ['thistestrunsthec', 'iphermul', 'tipletim']

    out1 = ''
    for s in input:
      out1 += method(c1, s)

    out2 = method(c2, ''.join(input))
    self.failUnlessEqual(out1, out2)


class NewdesTests(GenericTests):
  def test_block(self):
    self.cipher_encdec(
        newdes.newdes("0123456789abcde"),
        "01234567",
        unhexlify('f4702dca75d032fe'))

  def test_ecb(self):
    self.cipher_encdec(
        newdes.newdes("ihavethreeballs"),
        "testtest" * 4,
        unhexlify('7c69b602263f75f9') * 4)

  def test_cbc(self):
    self.cipher_encdec(
        newdes.newdes("nottoothrilling", IV="generous"),
        "gumballs" * 4,
        unhexlify('be475b3b09f636407767f0a6f9219b99093c5ab755c10a8a78d0d85eb8b32e51'))

  def test_split_cbc(self):
    self.cipher_split(
        newdes.newdes("nottoothrilling", IV="generous"),
        newdes.newdes.encrypt)
    self.cipher_split(
        newdes.newdes("nottoothrilling", IV="generous"),
        newdes.newdes.decrypt)


class Newdes96Tests(GenericTests):
  def test_block(self):
    self.cipher_encdec(
        newdes.newdes96(unhexlify('94266438e06c02e522256b64ed8c83')),
        unhexlify('e44a0435174eaa65'),
        unhexlify('488c387ea2fddd97'))

  def test_ecb(self):
    self.cipher_encdec(
        newdes.newdes96("bangingthegangs"),
        "elephant" * 4,
        unhexlify('d930b2ad7cb06530') * 4)

  def test_cbc(self):
    self.cipher_encdec(
        newdes.newdes96("veryunfortunate", IV="nomonkey"),
        "testtest" * 4,
        unhexlify('aa4122d23fc219a4c9629b6e64837704ed9312abfa87ef0a9321c4a826968e53'))

  def test_split_cbc(self):
    self.cipher_split(
        newdes.newdes96("nottoothrilling", IV="generous"),
        newdes.newdes96.encrypt)
    self.cipher_split(
        newdes.newdes96("nottoothrilling", IV="generous"),
        newdes.newdes96.decrypt)


if __name__ == '__main__':
  unittest.main()

