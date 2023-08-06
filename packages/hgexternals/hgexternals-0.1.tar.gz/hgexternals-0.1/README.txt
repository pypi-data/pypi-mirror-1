===========
hgexternals
===========

hgexternals is a Mercurial extension that simulates in some ways
Subversion's externals features.

To enable the `hgexternals` extension, create an entry for it in
your hgrc file, like this::

    [extensions]
    hgexternals =

Next create an EXTERNALS file in your repository containing a list of
projects you want to pull localy

Each line of the file contains:

1. the name of the directory where the external repository will be cloned
2. the repository url
3. the name of the VCS (optional). Currently supported : hg and svn.
   if not provided, hg is picked by default.

Example of an `EXTERNALS` file::

    FormAlchemy https://formalchemy.googlecode.com/hg
    WebTest http://svn.pythonpaste.org/Paste/WebTest/trunk svn

You can then use it by calling the `externals` command with the file in
argument::

    $ hg externals EXTERNALS

This will check out every repository described in the EXTERNALS
file its the directory. Everytime you call it, it will update
any existing check out.

Notice that you can also pass a directory, the extension will
look for a file name `EXTERNALS` in it::

    $ hg externals .     # looks in the current dir
    $ hg externals src     # looks in the src dir

Feedback is welcome !

- project page: http://bitbucket.org/tarek/hgexternals
- bug tracker: http://bitbucket.org/tarek/hgexternals/issues

