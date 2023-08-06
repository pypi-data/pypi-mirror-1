Taglist generator for findlinks
===============================

``tha.taglist`` generates an html list of svn tags suitable for
zc.buildout's find-links.

This package was originally developed for `The Health Agency
<http://www.thehealthagency.com>`_.  We're now using an alternative: generate
the sdist eggs into a pypi-like structure.  See `tha.sdistmaker
<http://pypi.python.org/pypi/tha.sdistmaker>`_


Installation
------------

Installation is the normal buildout procedure.

Some functionality from older versions (the actual finding of tags in svn) was
splitted out into a separate library, tha.tagfinder.


How it works
------------

The script iterates over the ``BASE`` repository as defined in
tha/taglist/defaults.py.  It first tries to use ``BASE_ON_SERVER``,
which you can use to define ``file:///svn`` as an alternative base
when available, which speeds it up on the server and which also makes
it usable for every user account.  It has a blacklist of directories
it won't interate into.  Every directory is examined for "stop
indicators" like ``setup.py`` that indicate that there aren't any
useful tag directories further down. See defaults.py for documentation
on how to override it in your buildout.

If a ``tags/`` directory is found an entry in the packages.html is
added with:

* The tag ('1.0'). We do a regex search for the version in the
  setup.py. If found and if it doesn't match the tag, we emit a
  warning.

* The svn url.

* The name that is extracted (with a regex) from the setup.py.

You can start the script with '-v' or '-vv' for more verbose logging.


Credits
-------

Made by `Reinout van Rees <http://reinout.vanrees.org>`_ at `The Health Agency
<http://www.thehealthagency.com>`_. 
