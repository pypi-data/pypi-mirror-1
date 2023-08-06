#!/usr/bin/env python

import unittest
import os.path

#### FIXME: this is a hack to get relative imports working
import os, sys
pathname = os.path.dirname(sys.argv[0])
fullpath = os.path.abspath(os.path.join(pathname, '..'))
sys.path.append(fullpath)
####

from openkremlin import util


class PathSanitizationTests(unittest.TestCase):
  def test_absolute(self):
    self.failUnlessEqual(util.sanitize_path('c:'), None)
    self.failUnlessEqual(util.sanitize_path('D:/'), None)
    self.failUnlessEqual(util.sanitize_path('Z:spam/eggs.txt'), 'eggs.txt')
    self.failUnlessEqual(util.sanitize_path('Z:\\spam\\eggs.txt'), 'eggs.txt')
    self.failUnlessEqual(util.sanitize_path('/also/an/absolute/path/'), 'path')

  def test_relative(self):
    self.failUnlessEqual(util.sanitize_path('spam.txt'), 'spam.txt')
    self.failUnlessEqual(util.sanitize_path('../../../windows/system32/kernel32.dll'), os.path.join('windows', 'system32', 'kernel32.dll'))
    self.failUnlessEqual(util.sanitize_path('eggs/./eggs/..../eggs/spam.txt'), os.path.join('eggs', 'eggs', 'eggs', 'spam.txt'))
    self.failUnlessEqual(util.sanitize_path('eggs/./eggs/...../eggs/spam.txt'), os.path.join('eggs', 'eggs', 'eggs', 'spam.txt'))

  def test_forks(self):
    self.failUnlessEqual(util.sanitize_path('c:\\spam\\eggs.txt:hello_i_am_a_fork'), 'eggs.txt')
    self.failUnlessEqual(util.sanitize_path('spam.txt:e/gg/s'), 'spam.txt')
    self.failUnlessEqual(util.sanitize_path('spam.txt::::eggs'), 'spam.txt')
    self.failUnlessEqual(util.sanitize_path(':unsalvageable_fork_syntax'), None)

  def test_magic_names(self):
    self.failUnlessEqual(util.sanitize_path('$eggs.txt'), '_$eggs.txt')
    self.failUnlessEqual(util.sanitize_path('c:\\$eggs.txt'), '_$eggs.txt')
    self.failUnlessEqual(util.sanitize_path('c:\\$spam\\eggs.txt'), 'eggs.txt')
    self.failUnlessEqual(util.sanitize_path('$spam\\eggs.txt'), os.path.join('_$spam', 'eggs.txt'))
    self.failUnlessEqual(util.sanitize_path('$'), '_$')

  def test_combined(self):
    self.failUnlessEqual(util.sanitize_path('/spam/eggs.txt/..'), None)
    self.failUnlessEqual(util.sanitize_path('/spam/eggs.txt:/..'), 'eggs.txt')

    self.failUnlessEqual(util.sanitize_path('c:/.'), None)
    self.failUnlessEqual(util.sanitize_path('c:/:unsalvageable_fork_syntax'), None)
    self.failUnlessEqual(util.sanitize_path('c:/../:::unsalvageable_fork_syntax'), None)
    self.failUnlessEqual(util.sanitize_path('c:../spam/eggs:::unsalvageable_fork_syntax'), 'eggs')
    self.failUnlessEqual(util.sanitize_path('../spam/eggs:::unsalvageable_fork_syntax'), os.path.join('spam', 'eggs'))

if __name__ == '__main__':
  unittest.main()

