z3c.recipe.epydoc
====================

Introduction
------------

This buildout recipe generates epydoc documentation for you project

Usage Instructions
------------------

Let's say you have a package called ezineserver. In the buildout.cfg file of your package, add a ``docs`` section
that looks like this::

  [docs]
  recipe = z3c.recipe.epydoc
  eggs = 
  	z3c.recipe.epydoc
  	ezineserver
  doc = ezineserver

Be sure to include it in the parts, as in::

  [buildout]
  develop = .
  parts = docs

Now you can rerun buildout.  The recipe will have created an
executable script in the bin directory called ``docs``.

This script will run the epydoc documentation generation tool on your
source code. 

To generate documentation simply run ``docs`` script::

  $ ./bin/docs

This generates all the documentation for you and placed it in the
parts directory.  You can then open it up in firefox and take a look::

  $ firefox parts/docs/index.html

And that's it!


Specify additional options
--------------------------

It's also possible to pass additional epydoc options to the ``docs`` script (for
a list of all available options, run the script with the ``--help`` option).

You can do this from two different ways:

  * you can pass options directly to the script::

      $ ./bin/docs --no-frames --include-log

  * or you can use the ``defaults`` entry to the ``docs`` section::

      [docs]
      recipe = z3c.recipe.epydoc
      eggs =
        z3c.recipe.epydoc
        ezineserver
      doc = ezineserver
      defaults = ['no-frames', '--include-log']

    This allows you to create a script with the same options as if you had
    specified them on the command line.

    If not set, the ``defaults`` entry will default to the value ``['-v',
    '--debug']``.
