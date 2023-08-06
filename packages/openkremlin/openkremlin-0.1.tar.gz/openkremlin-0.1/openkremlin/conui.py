"""The console user interface of OpenKremlin.
"""

import sys
import os
import getpass

from openkremlin import libkgb
from openkremlin import util

help_screen = \
"""usage: %s [options] FILENAME

options:
  --no-halt     Don't halt on errors (Windows-only)
  --traceback   Print full traceback one errors (for reporting bugs)
"""

class UIError(Exception):
  """Exception for errors generated in the user interface."""
  pass

class DummyFile(object):
  """Dummy "writable file" class for skipping files."""
  # FIXME: remove this hack later
  def write(self, buffer):
    pass
  def close(self):
    pass

class ConUI(object):
  def __init__(self):
    self.filename = None

    # --traceback switch; print full traceback on errors?
    self.traceback = False

    if os.name == 'nt':
      # halt on Windows by default to avoid closing of the command line window
      self.errhalt = True
    else:
      self.errhalt = False

  def run(self, args):
    try:
      self.parse_args(args[1:])
    except UIError, err:
      print str(err)
      print help_screen % args[0]
      sys.exit(1)

    try:
      self.open_archive()
      self.prompt_passphrase()
      self.decrypt_files()

    except Exception, err:
      if self.traceback:
        import traceback
        traceback.print_exc(file=sys.stderr)
      print str(err)

      if self.errhalt:
        # only on Windows
        import msvcrt
        raw_input("Press any key to exit.")
        msvcrt.getch()

      sys.exit(1)

    print "All done!"

  def parse_args(self, args):
    files = []
    for arg in args:
      if arg.startswith('-'):
        if arg == '--no-halt':
          self.errhalt = False
        elif arg == '--traceback':
          self.traceback = True
        else:
          raise UIError, "Unrecognized argument: '%s'" % arg
      else:
        files.append(arg)

    if len(files) < 1:
      raise UIError, "Archive name not specified"
    elif len(files) > 1:
      print "Warning: ignoring redundant arguments"

    self.filename = files[0]

  def open_archive(self):
    file = open(self.filename, 'rb')
    self.archive = libkgb.KgbArchive(file)

  def prompt_passphrase(self):
    while True:
      key = getpass.getpass("Enter archive passphrase (not displayed): ")
      ok = self.archive.set_passphrase(key)
      if ok:
        print "Passphrase OK"
        break
      else:
        print "Incorrect passphrase, please try again (or type Ctrl+C to quit)"

  def decrypt_files(self):
    print
    print "Decrypting files..."

    for envelope, metadata in self.archive.iter_entries():
      self.decrypt_single_file(envelope, metadata)

  def decrypt_single_file(self, envelope, metadata):
    filename, outfile = self.open_outfile(metadata)
    self.output_current_file(filename, metadata)

    try:
      self.archive.decrypt_file(metadata, envelope, outfile, self.update_progress)
    finally:
      # the progress bar doesn't print a newline so we need to terminate that
      sys.stdout.write('\n')
    outfile.close()

  def open_outfile(self, metadata):
    # looks like this function needs some refactoring soon, but it will have
    # to do for now

    filename = util.sanitize_path(metadata[0])
    if metadata[1] == 0:
      # zero-length files denote directories; directories *always* come after
      # their contents so we just ignore it
      return filename, DummyFile()

    self.create_dir(filename)

    # handle filename conflict
    if filename is not None and os.path.exists(filename):
      print "File '%s' already exists." % filename

      # loop until the user makes a legitimate choice
      while True:
        choice = raw_input("[o]verwrite [r]ename [s]kip: ").lower()

        if choice == 'o':
          break
        elif choice == 'r':
          filename = None
          break
        elif choice == 's':
          return '(skipping)', DummyFile()

    # loop until supplied filename can be opened
    while True:
      if filename is None:
        filename = raw_input("Please enter new filename: ")

      try:
        outfile = open(filename, 'wb')
        return filename, outfile
      except (IOError, OSError), err:
        print "Cannot open file: %s" % err
        filename = None

  def create_dir(self, filename):
    """Create directory for the file if necessary."""

    dir = os.path.dirname(filename)
    if dir and not os.path.exists(dir):
      print 'Creating directory %s' % dir
      os.makedirs(dir)

  # visual interface
  def output_current_file(self, filename, metadata):
    if len(filename) <= 20:
      self.progress_prefix = "%-20s %s " % (filename, util.format_bytes(metadata[1]))
    else:
      # progress bar doesn't fit on the same line
      print filename
      self.progress_prefix = "    %s " % util.format_bytes(metadata[1])

  def update_progress(self, completed, total):
    columns = 79 - len(self.progress_prefix) - 9
    if total == 0:
      # avoid division by zero
      completed = total = 1

    bars = (columns * completed) // total
    percentage = (100.0 * completed) / total

    sys.stdout.write("\r%s[%s%s] %5.1f%%" % (self.progress_prefix,
      '#' * bars, ' ' * (columns-bars), percentage))
    sys.stdout.flush()


def main():
  try:
    ui = ConUI()
    ui.run(sys.argv)
  except KeyboardInterrupt:
    sys.exit(1)

if __name__=='__main__':
  main()

