GtkEggDeps
==========

GtkEggDeps uses the wonderful tl.eggdeps and PyGtk to provide an interactive
dependency browser.


Installation
------------

If you have easy_install, you should be able to easy_install gtkeggdeps.

Alternatively, download gtkeggdeps.py and use it directly. You'll need to have
tl.eggdeps installed.

The source code can be found in this Bazaar repository:
http://mg.pov.lt/gtkeggdeps/bzr

The project home page is at http://mg.pov.lt/gtkeggdeps


Usage
-----

You can pass a list of egg names on the command line to limit the view just to
those eggs and their dependencies.  You can also specify package names to
completely ignore.  Run gtkeggdepps --help for the syntax.

The standard Gtk+ keys for navigating trees are

=========== ================================================================
'+'         expand a tree node
'-' or '/'  collapse a tree node
'*'         expand a tree node recursively
Backspace   jump to parent
Ctrl+S      start incremental search among expanded nodes
Ctrl+Up     find previous matching node
Ctrl+Down   find next matching node
=========== ================================================================

Extra keys defined by gtkeggdeps

=========== ================================================================
Enter       expand/collapse a node
=========== ================================================================

The colours are:

=========== ================================================================
red         This is a dependency loop
blue        There exists a dependency to this package that is less indirect
            (e.g. if z3c.formdemo directly depends on zope.schema, then
            whenever zope.schema appears as an indirect dependency it will
            be in blue).  Blue nodes aren't expanded recursively when you
            press '*', but they can be expanded with '+'.
grey        This package is not available in your working set
=========== ================================================================

The meaning of brackets are:

=========== ================================================================
(name)      This package is incompatible with the rest (due to a version
            conflict somewhere)
{name}      This package is not available
=========== ================================================================


Usage with zc.buildout
----------------------

Add a new part to buildout.cfg that uses zc.recipe.egg and installs gtkeggdeps
together with the eggs whose dependencies you want to explore. Example for
z3c.formdemo::

    [buildout]
    develop = .
    parts = demo test coverage eggdeps

    [eggdeps]
    recipe = zc.recipe.egg
    eggs = gtkeggdeps
           z3c.formdemo [app, test]

    ...

Rerun buildout and you'll get a bin/gtkeggdeps script that will see all the
eggs you specified.


Known bugs
----------

* If there's a dependency loop and there are no packages depending on at
  least one package participating in that loop, the whole loop will be
  excluded from the output

