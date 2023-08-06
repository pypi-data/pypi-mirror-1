OpenKremlin
===========

OpenKremlin is a free software/open source program to decrypt .kgb archives
produced by the proprietary Kremlin Encrypt cryptography product. OpenKermlin
is written in the Python programming language and is licensed under the
permissive MIT license.

NB! OpenKremlin 0.2 is beta quality software; there are probably unfixed bugs
left in the program.

OpenKremlin is currently hosted at Bitbucket:
http://bitbucket.org/nonguru/openkremlin/

Latest changes are always available from OpenKremlin Mercurial repository:
http://bitbucket.org/nonguru/openkremlin/overview/

IMPORTANT WARNING
-----------------

The current prerelease version of OpenKremlin does NOT wipe encryption keys
from memory after use. This means that there is a small chance that encryption
keys, or the plaintext itself, could be written to the swap file by the
operating system. This is not unqiue to OpenKremlin; if you expose
un-encrypted files to any normal application -- like file managers, editors,
viewers, etc -- there is always a significant risk of leaking data to the swap
space.

IF YOU ARE WORKING WITH CONFIDENTIAL DATA OF ANY KIND, ENCRYPTED SWAP SPACE IS
OBLIGATORY (or no swap at all).

Prerequisites
-------------

If you are using the prebuilt Windows installer, all dependencies are already
bundled.

Otherwise, you also need the following software packages:

* Python 2.3 or newer, from http://www.python.org/
* PyCrypto, from http://www.amk.ca/python/code/crypto
  (windows binaries at
  http://www.voidspace.org.uk/python/modules.shtml#pycrypto)

Usage
-----

On FreeBSD you can install archivers/py-openkremlin from ports and run:
  unkgb filename.kgb

On other Unix-like operating systems, just run unkgb.py with the .kgb file as
an argument:
  /path/to/unkgb.py filename.kgb

On Windows, the installer automatically registers the .kgb extension.

For information on building the Windows installer, see READMEWIN32.txt

Feedback
--------

Please report any problems you encounter, or any ideas for improvements, to
the OpenKremlin bug tracker: 
  http://bitbucket.org/nonguru/openkremlin/issues/new/

(TODO: explain how to obtain the Python backtrace for exceptions)

Thanks
------

Thanks to Mixie for:
 * Figuring out how to make the Windows installer
 * Windows icon
 * Emotional support -- I would have never done it without your repeated
   status inquiries ;)

