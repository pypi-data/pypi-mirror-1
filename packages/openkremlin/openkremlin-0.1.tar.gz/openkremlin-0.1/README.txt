OpenKremlin
===========

OpenKremlin is a free software/open source program to decrypt .kgb archives
produced by the proprietary Kremlin Encrypt cryptography product. OpenKermlin
is written in the Python programming language and is licensed under the
permissive MIT license.

NB! OpenKremlin 0.1 is alpha quality software; some features are missing or do
not work properly. Please refer to the TODO file.

OpenKremlin is currently hosted at ShareSource:
http://sharesource.org/project/openkremlin/

Latest changes are always available from OpenKremlin Mercurial repository:
http://hg.sharesource.org/openkremlin/

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
  http://sharesource.org/project/openkremlin/bugs/report/

(TODO: explain how to obtain the Python backtrace for exceptions)

Thanks
------

Thanks to Mixie for:
 * Figuring out how to make the Windows installer
 * Windows icon
 * Emotional support -- I would have never done it without your repeated
   status inquiries ;)

