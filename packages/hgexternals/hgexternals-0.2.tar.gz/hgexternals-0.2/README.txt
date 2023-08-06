===========
hgexternals
===========

hgexternals is a Mercurial extension that simulates in some ways
Subversion's externals features.

To enable the "hgexternals" extension, either shipped with Mercurial or
in the Python search path, create an entry for it in your hgrc, like this::


    [extensions]
    hgexternals =

For help using hgexternals, run: "hg externals --help"


hg status hook
--------------

You can also expand your stat command by adding hook::


    [hooks]
    post-status = python:hgexternals.extstatushook

It will display externals status similar way Subversion does.

Currently extstatushook does not recognize any option specific to hg stat. It
should support global options as --repo. It will warn you that option is not
recognized and wont produce output. Hovever **it does support** nodes on which
should stat be ran.

.. warning::

    From this version EXTERNALS or .hgexternals can be placed **ONLY** in
    repository root.


Reporting bugs
--------------

Please report bugs at http://bitbucket.org/tarek/hgexternals/
