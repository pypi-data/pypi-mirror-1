"""The console user interface of OpenKremlin.
"""

import sys
import os
import getpass

from openkremlin import libkgb
from openkremlin import util

tkgui = None # imported lazily

help_screen = \
"""usage: %s [options] FILENAME

options:
  --no-halt     Don't halt on errors (Windows-only)
  --console     Force console mode; don't try to spawn GUI
  --traceback   Print full traceback on errors (for reporting bugs)
"""

class UIError(Exception):
  """Exception for errors generated in the user interface."""
  pass

class SkipFile(Exception):
  pass

class ConUI(object):
  def __init__(self):
    self.filename = None

    self.console = False
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

      if not self.console:
        self.try_import_tkgui()
        if not self.filename:
          self.get_file()

      if not self.filename:
        raise UIError, "Archive name not specified"
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
      if isinstance(err, EOFError):
        print "Unexpected end of file."
      else:
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
        elif arg == '--console':
          self.console = True
        else:
          raise UIError, "Unrecognized argument: '%s'" % arg
      else:
        files.append(arg)

    if len(files) > 1:
      print "Warning: ignoring redundant arguments"

    if files:
      self.filename = files[0]

  def try_import_tkgui(self):
    if self.console:
      return

    try:
      global tkgui
      from openkremlin import tkgui

    except util.GuiError, err:
      print "Warning: cannot import graphical interface: " + str(err)
      if self.traceback:
        raise
      self.console = True

  def get_file(self):
    if not tkgui:
      return

    try:
      self.filename = tkgui.choose_file()

      if self.filename:
        # change directory so that files are extracted to the right place
        os.chdir(os.path.dirname(self.filename))
    except util.GuiError, err:
      print "Warning: cannot launch file chooser: " + str(err)

  def open_archive(self):
    file = open(self.filename, 'rb')
    self.archive = libkgb.KgbArchive(file)

  def prompt_passphrase(self):
    """Prompts the user for a passphrase.
    
    Unless --console was supplied, attempts to spawn the GUI version of getpass
    first. On failure, falls back to console-based getpass."""

    if self.console:
      self.console_getpass()
      return

    try:
      key = tkgui.getpass(self.archive.set_passphrase)

    except util.GuiError, err:
      print "Warning: Cannot spawn graphical getpass: " + str(err)
      if self.traceback:
        raise

      self.console_getpass()
      return

    if key is None:
      print "Cancelled"
      raise sys.exit()
    else:
      self.archive.set_passphrase(key)

  def console_getpass(self):
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

    for entry in self.archive.iter_entries():
      try:
        self.decrypt_single_file(entry)
      except SkipFile:
        pass

  def decrypt_single_file(self, entry):
    filename, outfile = self.open_outfile(entry)
    self.output_current_file(filename, entry)

    try:
      entry.decrypt(outfile, self.update_progress)
    finally:
      # the progress bar doesn't print a newline so we need to terminate that
      sys.stdout.write('\n')
    outfile.close()

  def open_outfile(self, entry):
    # looks like this function needs some refactoring soon, but it will have
    # to do for now

    filename = util.sanitize_path(entry.filename)
    if entry.filesize == 0:
      # zero-length files denote directories; directories *always* come after
      # their contents so we just ignore it
      raise SkipFile

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
          raise SkipFile

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
  def output_current_file(self, filename, entry):
    if len(filename) <= 20:
      self.progress_prefix = "%-20s %s " % (filename, util.format_bytes(entry.filesize))
    else:
      # progress bar doesn't fit on the same line
      print filename
      self.progress_prefix = "    %s " % util.format_bytes(entry.filesize)

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

