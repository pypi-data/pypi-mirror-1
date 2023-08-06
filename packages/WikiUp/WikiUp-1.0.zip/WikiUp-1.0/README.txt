==================================================
Updating Project Wiki Pages from Docs using WikiUp
==================================================

The WikiUp project defines a setuptools extension to allow uploading Wiki
pages from source documentation.  It's primarily intended to be useful for
PEAK projects to update the PEAK Wiki, but other projects could make use of
the same basic framework.

Installing this project adds a ``wikiup`` command to setuptools-based packages.
By default, this command will read a file called ``wikiup.cfg`` in the project
directory containing content like this::

    [wikiname]
    pagename = filename

In other words, a file with a section for each wiki, and a pagename + filename
on each line.  (The filename is actually optional; if you just list a pagename
without an ``=``, the filename will be assumed to be the same as the page
name.)  Filenames must be relative to the setup directory, and use ``/`` as
a separator, as they will be converted to an OS path using the distutils
``convert_path()`` function.

To configure a Wiki, you need to add it to a distutils config file (usually
your ``$HOME/pydistutils.cfg`` or ``~/.pydistutils.cfg`` file) like so::

    [wikiup-wikiname]
    url = base url here
    type = plugin name here
    ... other settings, if any

In other words, for each wiki, you need a ``[wikiup-foo]`` section, where
``foo`` is the name of the wiki as it will appear in some project's
``wikiup.cfg`` file.

The ``url`` is the Wiki's base URL, and ``type`` is the name of the plugin to
be used to do the uploading.  Currently, the only supported value for ``type``
is ``OldMoin``, which works with the old MoinMoin wiki used by the PEAK
projects.


Command-Line Usage
------------------

The ``setup.py wikiup`` command optionally takes a ``--comment`` or ``-c``
option to specify an update comment to apply when editing.  It can also be
given ``--config-file`` or ``-C`` to specify an alternate config file in place
of the local ``wikiup.cfg`` file.


The ``OldMoin`` Plugin
----------------------

The ``OldMoin`` plugin takes two optional arguments in its configuration
section, in addition to the required ``type`` and ``url``::

    [wikiup-foo]

    type = OldMoin
    url = something

    uid = login.id.goes.here
    page_format = {{{ %s }}}

The ``uid`` allows you to specify a MoinMoin login ID to use; if specified,
the plugin will use the ``userform`` Wiki action to log in as that ID before
uploading any pages.

The ``page_format`` is a format string (defaulting to ``"#format rst\n%s"``)
that will be used to convert the raw upload file into the page text that will
be posted to the wiki.  The string is interpreted using the ``string_escape``
codec, so you will need to double-up on backslashes to keep them from being
treated as character escapes.


Adding Plugins
--------------

You can implement alternative plugins for other wiki types, by subclassing
``wikiup.Wiki`` and registering the resulting class in the ``wikiup.plugins``
entry point group.  See the source code for details of what the plugin must be
able to do.


Support
-------

Questions, comments, and bug reports for this package should be directed to the
`PEAK mailing list`_.

.. _PEAK mailing list: http://www.eby-sarna.com/mailman/listinfo/peak/

