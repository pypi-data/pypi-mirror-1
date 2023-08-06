Building and creating the installer for Windows
-----------------------------------------------

To build:
You need python installed, and the pycrypto modules.
Python is available from here:
http://www.python.org/
pycrypto is available here:
http://www.amk.ca/python/code/crypto
There are also pre-built binaries of pycrypto
 for Win32 available here:
http://www.voidspace.org.uk/python/modules.shtml#pycrypto

You also need the py2exe distutils extension:
http://www.py2exe.org/

To create the installer, you need Inno Setup.
http://www.jrsoftware.org/isinfo.php

Once you have those you are ready to build.
chdir to the directory that contains setup.py.
Enter the following command.

setup.py py2exe

This will compile Win32 binaries and collect all the dependancies in
the "dist" directory. Open setup.iss in Inno Setup
and compile it by choosing "Build -> Compile" from the menus. The
installer will be created in the Output directory.
