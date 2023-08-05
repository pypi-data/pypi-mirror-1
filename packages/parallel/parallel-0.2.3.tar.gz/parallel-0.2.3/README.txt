Introduction
------------

The pprocess module provides elementary support for parallel programming in
Python using a fork-based process creation model in conjunction with a
channel-based communications model implemented using socketpair and poll. On
systems with multiple CPUs or multicore CPUs, processes should take advantage
of as many CPUs or cores as the operating system permits.

Quick Start
-----------

Try running the simple example:

PYTHONPATH=. python examples/simple.py

(A simple example which shows how a limited number of processes can be used to
perform a parallel computation.)

Or studying some elementary tests:

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

Some examples are also found in the examples directory, notably the PyGmy
raytracer modified to use pprocess:

cd examples/PyGmy
PYTHONPATH=../..:. python scene.py

(This should produce a file called test.tif - a TIFF file containing a
raytraced scene image.)

Contact, Copyright and Licence Information
------------------------------------------

No Web page has yet been made available for this work, but the author can be
contacted at the following e-mail address:

paul@boddie.org.uk

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt and docs/LICENCE.txt for more information.

For the PyGmy raytracer example, different copyright and licence information
is provided in the docs directory - see docs/COPYING-PyGmy.txt and
docs/LICENCE-PyGmy.txt for more information.

Dependencies
------------

This software depends on standard library features which are stated as being
available only on "UNIX"; it has only been tested on a GNU/Linux system.

New in parallel 0.2.3 (Changes since parallel 0.2.2)
----------------------------------------------------

  * Added convenient message exchanges, offering methods handling common
    situations at the cost of having to define a subclass of Exchange.
  * Added a simple example of performing a parallel computation.
  * Improved the PyGmy raytracer example to use the newly added functionality.

New in parallel 0.2.2 (Changes since parallel 0.2.1)
----------------------------------------------------

  * Changed the status testing in the Exchange class, potentially fixing the
    premature closure of channels before all data was read.
  * Fixed the PyGmy raytracer example's process accounting by relying on the
    possibly more reliable Exchange behaviour, whilst also preventing
    erroneous creation of "out of bounds" processes.
  * Added a removed attribute on the Exchange to record which channels were
    removed in the last call to the ready method.

New in parallel 0.2.1 (Changes since parallel 0.2)
--------------------------------------------------

  * Added a PyGmy raytracer example.
  * Updated copyright and licensing details (FSF address, additional works).

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
Update PyPI.

Making Packages
---------------

To make Debian-based packages:

  1. Create new package directories under packages if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/ubuntu-hoary/python2.4-parallel-pprocess/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
