sdistmaker
==========

Create sdist tarballs from svn tags, intended for use with a company-internal
svn repository.  Creates sdist tarballs into a directory you can then serve
with apache.

sdistmaker used to be called tha.sdistmaker before version 1.2.


Installation and basic usage
----------------------------

A simple ``easy_install sdistmaker`` is enough.  This gives you two scripts:

- ``make_sdist``, mainly for test purposes.  Pass it an svn tag url and a
  destination dir and it will make a release.

- ``sdists_from_tags`` is the main script.  It searches an svn structure for
  suitable tags and makes releases of them.

For starters, just run ``sdists_from_tags``.  It will create a ``var/private``
directory and fill it with (as an example!) all zest.releaser releases.

Both scripts have a ``--help`` option that show all available options and a
usage instruction.


Configuration
-------------

Configuration is by means of a python file.  Easiest way to get started is by
printing sdistmaker's own base defaults.py by doing::

  $> sdists_from_tags --print-example_defaults

Save the output as a python file (suggestion: defaults.py).  You can then
adapt it to your liking and use it with ``sdists_from_tags
--defaults-file=defaults.py``.  The defaults file is documented in-line, so it
should be easy to adapt.


Usage in a buildout
-------------------

You can use sdistmaker in a buildout like this::

    [buildout]
    parts = sdists

    [sdists]
    recipe = zc.recipe.egg
    eggs = sdistmaker
    scripts = sdists_from_tags
    # arguments =
    #     defaults_file='${buildout:directory}/defaults.py',

The ``defaults.py`` is created in the same way as above.


Using sdistmaker in combination with the real pypi
--------------------------------------------------

A structure like generated with sdistmaker is a perfect index for easy_install
and buildout if you let apache host it.  Only problem: you can only have one
index (note: pip apparently supports multiple indexes).  You can solve this
problem by having apache redirect you to pypi when something is not found.

Here's an example apache config snippet::

  # Allow indexing
  Options +Indexes
  IndexOptions FancyIndexing VersionSort

  # Start of rewriterules to use our own var/private/* packages
  # when available and to redirect to pypi if not.
  RewriteEngine On
  # Use our robots.txt:
  RewriteRule ^/robots.txt - [L]
  # Use our apache's icons:
  RewriteRule ^/icons/.* - [L]
  # We want OUR index.  Specified in a weird way as apache
  # searches in a weird way for index.htm index.html index.php etc.
  RewriteRule ^/index\..* - [L]

  # Use our var/private/PROJECTNAME if available,
  # redirect to pypi otherwise:
  RewriteCond /path/on/server/var/private/$1 !-f
  RewriteCond /path/on/server/var/private/$1 !-d
  RewriteRule ^/([^/]+)/?$ http://pypi.python.org/pypi/$1/ [P,L]

  # Use our var/private/PROJECTNAME/project-0.1.tar.gz if available,
  # redirect to pypi otherwise:
  RewriteCond /path/on/server/var/private/$1 !-d
  RewriteRule ^/([^/]+)/([^/]+)$ http://pypi.python.org/pypi/$1/$2 [P,L]

You can use such a custom index in two ways.  Easy_install has a ``-i`` option
for passing along an index::

  $> easy_install -i http://packages.my.server/ zest.releaser

In buildout, you can set it like this::

  [buildout]
  index = http://packages.my.server/
  parts =
      ...



Reporting bugs
--------------

You can report bugs or feature requests at
http://bitbucket.org/reinout/sdistmaker/issues/


Credits
-------

Written by `Reinout van Rees <http://reinout.vanrees.org>`_. Started while at
`The Health Agency <http://www.thehealthagency.com>`_, improved at `Nelen &
Schuurmans <http://www.nelen-schuurmans.nl>`_.
