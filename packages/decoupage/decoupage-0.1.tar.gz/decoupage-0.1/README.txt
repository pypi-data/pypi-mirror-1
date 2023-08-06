decoupage
=========

what is it?
-----------

decoupage is a static file server that allows for index pages
configurable with genshi templates and .ini files.  I mainly wrote it
because i was tired of using apache for serving my website and
generating index.html files by hand.


how do i use it?
----------------

Set up a `paste <http://pythonpaste.org>` .ini file that specifies the
directory to serve (``decoupage.directory``) and, optionally, a
configuration file .ini file (``decoupage.configuraton``) which
specifies the labels for the files based on directory. An example of a
`paste <http://pythonpaste.org>` .ini file is in
``decoupage.ini``. Note the ``[app:decoupage]`` section::

    [app:decoupage]
    paste.app_factory = decoupage.factory:factory
    decoupage.directory = %(here)s/example
    decoupage.configuration = %(here)s/example.ini

The labels for files are in ``example.ini``, specified by sections as
directories::

    [/]
    foo.txt = a file about cats

    [/cats]
    lilly.txt = lilly
    hobbes.txt = a file about Hobbes

You can specify the entire layout from here.  Alternately, you can
have an ``index.ini`` in a directory which, if present, overrides the
default configuration.  Such a file is in the ``fleem`` subdirectory
of ``example``::

    /template = index.html
    fleem.txt = some fleem for ya

Try it out!  Install decoupage and run ``paster serve decoupage.ini``
and point your browser to the URL it gives you.


how do i do more with decoupage?
--------------------------------

Since filenames can't start with a ``/`` (just try it!), the
functionality of decoupage may be extended with ``/`` commands in a
section.  The only one currently implemented is ``/template`` (see
above for the case in ``example/fleem``) which will use a custom
template for that section.  I plan to make this pluggable with
setuptools ``entry_points``, and cascadable as well.  But that's for
later, probably when I need it.  In the mean time, I have a disc to
recover and a website to set up.



