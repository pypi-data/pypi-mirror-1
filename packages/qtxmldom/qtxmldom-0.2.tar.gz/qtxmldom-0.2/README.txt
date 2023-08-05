Introduction
------------

See docs/index.html for the qtxmldom documentation.

Contact, Copyright and Licence Information
------------------------------------------

The current Web page for qtxmldom at the time of release is:

http://www.boddie.org.uk/python/qtxmldom.html

Copyright and licence information can be found in the docs directory - see
docs/COPYING.txt for more information.

Dependencies
------------

PyQt        Tested with PyQt 3.15 (although releases from 3.8.1 have been
            known to work).
PyKDE       Tested with the PyKDE 20050829 snapshot (although releases from
            3.8.0 have been known to work).
            This dependency is optional since qtxmldom only requires PyKDE to
            be able to provide KHTML DOM support.
Python      Tested with Python 2.4.
            Python releases from 2.2 onwards should be compatible with
            qtxmldom. The principal requirement from such releases is the
            new-style class support which permits the use of properties in
            the qtxmldom implementation.

Testing
-------

The tests directory contains scripts which exercise qtxml and KHTML somewhat.

Issues
------

Much more work needs to be done to cover the features of the qtxml and KHTML
DOM APIs, particularly support for ranges and other novel features which many
Python XML toolkits do not seem to support.

Recommendations for Building PyKDE from Source
----------------------------------------------

On machines with small memory (these days, this is considered to be anything
as low as 128MB) where the PyKDE package is to be built from sources, it is
vital that the memory saving options are used with the build.py script:

python build.py -c-

It is also vital to check that the script actually obeys these options, which
was not the case with PyKDE 3.8.0. The following command will apply a patch to
the script in order to make it work correctly:

patch -p0 < qtxmldom/patches/PyKDE/build.py.diff

The command should be run outside/above the PyKDE-3.8.0 directory, and the
stated path should be adjusted accordingly.

New in qtxmldom 0.2 (Changes since qtxmldom 0.1)
------------------------------------------------------

  * Added createDocument and createDocumentType methods.
  * Added convenience functions for obtaining qtxmldom representations.
  * Added getElementsByTagName and related methods, along with the normalize
    method.
  * Fixed various string conversion issues.
  * Added the node types from xml.dom to the qtxml Node class itself.
  * Added the khtmlutils module for conversion of KHTML documents to
    libxml2dom (and potentially other DOM APIs).
  * Added some examples of KHTML document processing in KParts (in the
    examples directory).
  * Reorganised the documentation, expanding the README.txt file at the
    expense of the HTML documentation, but removing older, less relevant
    information.
  * Added Debian package support.

Release Procedures
------------------

Update the qtxmldom/__init__.py __version__ attribute.
Change the version number and package filename/directory in the documentation.
Change tests and code examples in the documentation if appropriate.
Update the release notes (see above).
Update the package release notes (in the packages directory).
Check the setup.py file and ensure that all package directories are mentioned.
Check the release information in the PKG-INFO file and in the package
changelog (and other files).
Tag, export.
Archive, upload.
Make packages (see below).
Update PyPI, PythonInfo Wiki, Vaults of Parnassus entries.

Making Packages
---------------

To make Debian packages:

  1. Create new package directories under packages/debian if necessary.
  2. Make a symbolic link in the distribution's root directory to keep the
     Debian tools happy:

     ln -s packages/debian/python2.4-qtxmldom/debian/

  3. Run the package builder:

     dpkg-buildpackage -rfakeroot

  4. Locate and tidy up the packages in the parent directory of the
     distribution's root directory.
