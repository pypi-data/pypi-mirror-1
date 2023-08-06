Introduction
============

This package installs a command-line python script and an emacs
command for exporting a GMail filters Atom feed from the gnus-public
and gnus-private fields in BBDB.

Installing
----------

The package can be installed using the standard python package
installation procedure.  Extract the tarball, then run the following
command inside the extracted directory::

    $ python setup.py install

This will install the command-line utility and the rpatterson-gmail.el
emacs library.  Then add the following to your ~/.emacs::

    (require 'rpatterson-gmail)

Usage
-----

Once installed, the filters can be exported to a file simply by
calling M-x bbdb-export-gmail-filters.  You will be prompted for a
file to export the filters to.

For every BBDB record that has a value in the gnus-private field, a
filter will be included that matches the "To" GMail filter field on
any BBDB net addresses for that record and applies the label specified
in the gnus-private field value.  The same is done for BBDB records
with values in the gnus-public BBDB field but filters on the "From"
GMail filter field instead.
