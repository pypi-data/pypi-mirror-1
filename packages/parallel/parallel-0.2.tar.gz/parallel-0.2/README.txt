Introduction
------------

The pprocess module provides elementary support for parallel programming in
Python using a fork-based process creation model in conjunction with a
channel-based communications model implemented using socketpair and poll.

Quick Start
-----------

Try running some of the tests:

PYTHONPATH=. python tests/create_loop.py
PYTHONPATH=. python tests/start_loop.py

(Simple loop demonstrations which use two different ways of creating and
starting the parallel processes.)

PYTHONPATH=. python tests/start_indexer.py <directory>

(A text indexing demonstration, where <directory> should be a directory
containing text files to be indexed, although HTML files will also work well
enough. After indexing the files, a prompt will appear, words or word
fragments can be entered, and matching words and their locations will be
shown. Run the program without arguments to see more information.)

Contact, Copyright and Licence Information
------------------------------------------

No Web page has yet been made available for this work, but the author can be
contacted at the following e-mail address:

paul@boddie.org.uk

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information.

Dependencies
------------

This software depends on standard library features which are stated as being
available only on "UNIX"; it has only been tested on a GNU/Linux system.

New in parallel 0.2 (Changes since parallel 0.1)
------------------------------------------------

  * Changed the name of the included module from parallel to pprocess in order
    to avoid naming conflicts with PyParallel.

Release Procedures
------------------

Update the pprocess __version__ attribute.
Change the version number and package filename/directory in the documentation.
Update the release notes (see above).
Check the release information in the PKG-INFO file.
Tag, export.
Archive, upload.
Update PyPI, PythonInfo Wiki, Vaults of Parnassus entries.

Making Packages
---------------

To make Debian packages:

  1. Create new package directories under packages/debian if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/debian/python2.4-parallel-pprocess/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
