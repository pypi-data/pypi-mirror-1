Taglist generator for findlinks
===============================

``tha.taglist`` generates an html list of svn tags suitable for
zc.buildout's find-links.

Installation
------------

Installation is the normal buildout procedure.



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
