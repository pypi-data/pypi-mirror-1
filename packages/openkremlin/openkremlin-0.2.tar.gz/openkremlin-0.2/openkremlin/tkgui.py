"""Tkinter-based graphical user interface for OpenKremlin.

For now, this module does not implement a full GUI. It is only called from
within conui (console UI) for prompting the password.

If import of the Tkinter module fails, util.GuiError is raised"""

import util     # has GuiError
try:
  import Tkinter
  import tkFileDialog
except ImportError, err:
  raise util.GuiError(str(err))


def choose_file():
  """Open a file dialog to choose a file"""

  filetypes = [
      ('Kremlin Encrypt files', '*.kgb'),
      ('All files', '*')]
  title = "Choose file to extract..."

  try:
    # You can't have a tkFileDialog without an empty root window popping up, so
    # instead hide it as quickly as possible.
    root = Tkinter.Tk()
    root.withdraw()

    file = tkFileDialog.askopenfilename(parent=root, title=title, filetypes=filetypes)
    root.destroy()
    if not file:
      return None
    return file
  except Tkinter.TclError, err:
    raise util.GuiError, str(err)


def getpass(try_pass_cb):
  """Spawns a Tkinter window and prompts for a passphrase. Returns passphrase
  as string, or None if cancel was pressed.
  
  Raises util.GuiError if there was a problem spawning the window; this can be
  handled to fall back to console-based getpass()"""

  try:
    root = Tkinter.Tk()
    getpass = GetPassDialog(root, try_pass_cb)
  except Tkinter.TclError, err:
    raise util.GuiError, str(err)

  root.mainloop()

  return getpass.retval

class GetPassDialog(Tkinter.Frame):
  """Simple password entry dialog."""

  def __init__(self, parent, try_pass_cb):
    Tkinter.Frame.__init__(self, borderwidth=8)
    self.parent = parent
    self.try_pass = try_pass_cb
    self.retval = None
    self.timer = None

    self.populate()

    self.try_clipboard()

  def populate(self):
    """Populates the frame with widgets."""

    self.parent.title("OpenKremlin passphrase")

    label = Tkinter.Label(self, text="Enter passphrase:")
    label.pack()
    self.passinput = Tkinter.Entry(self, width=30, show=u'\u25cf')
    self.passinput.focus_force()
    self.passinput.pack(expand='yes', fill='x')

    self.status_label = Tkinter.Label(self, text="")
    self.status_label.pack()

    self.okbutton = Tkinter.Button(self, text="OK", default='active',
        command=self.click_ok, width=6, height=1)
    self.okbutton.pack(side='left')

    print self.okbutton['width'], self.okbutton['height']

    self.cancelbutton = Tkinter.Button(self, text="Cancel",
        command=self.click_cancel, width=6, height=1)
    self.cancelbutton.pack(side='right')

    self.pack(expand='yes', fill='both')

    self.parent.bind('<Return>', self.click_ok)
    self.parent.bind('<Escape>', self.click_cancel)
    self.bind('<Destroy>', self.handle_destroy)

  def try_clipboard(self):
    """Tries to find the passphrase in the clipboard automatically"""

    # not implemented in Python 2.4 or earlier
    if not hasattr(self, 'clipboard_get'):
      return

    try:
      key = self.clipboard_get()
    except Tkinter.TclError, err:
      print "Warning: can't get clipboard: %s" % err
      return

    # sanity check: don't crash if the user has a whole novel in their clipboard
    key = key[:10000]

    if self.try_pass(key):
      self.clipboard_found(key)
      return

    key = key.strip()
    if self.try_pass(key):
      self.clipboard_found(key)

  def clipboard_found(self, key):
    self.passinput.delete(0, 'end')
    self.passinput.insert(0, key)
    self.display_notice("Found passphrase in clipboard", 'green')

  def click_ok(self, event=None):
    """'OK' button clicked or or 'Enter' pressed."""

    passphrase = self.passinput.get()

    if self.try_pass(passphrase):
      self.retval = passphrase
      self.parent.destroy()
    else:
      self.display_notice("Invalid passphrase", 'red')

  def click_cancel(self, event=None):
    """'Cancel' button clicked or 'Esc' pressed."""
    self.retval = None
    self.parent.destroy()

  def display_notice(self, text, color):
    """Display the "Invalid passphrase" notice"""

    if self.timer:
      self.after_cancel(self.timer)
      self.timer = None

    self.status_label['text'] = text
    self.status_label['bg'] = color

    # timed callback to reset the notice color
    def reset_color():
      self.status_label['bg'] = self['bg']

    self.timer = self.after(1000, reset_color)

  def handle_destroy(self, event):
    if self.timer:
      self.after_cancel(self.timer)
      self.timer = None


if __name__=='__main__':
  # if this file is invoked directly, run in testing mode
  ret = choose_file()
  print 'coose_file:', ret

  def try_pass(passphrase):
    print 'try_pass:', passphrase
    return False

  ret = getpass(try_pass)
  print 'return:', ret

