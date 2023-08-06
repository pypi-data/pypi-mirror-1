Development
===========

Tools
-----
director uses what is becoming a pretty standard and a quite simple toolset.


Required Tools
--------------
 #. `python <http://www.python.org>`_ - The python programming language or an alternate implementation (see bellow).
 #. `distutils <http://docs.python.org/lib/module-distutils.html>`_ - Python building and packaging library
 #. `git <http://git.or.cz/>`_ - Source code management 
 #. `an <http://www.vim.org>`_ `editor <http://www.gnu.org/software/emacs/>`_ or `ide <http://pida.co.uk/>`_ `that <http://scribes.sourceforge.net/>`_ doesn't suck


Python Implementations
----------------------

+-------------------------------------------------------------------------------------+----------------------------+-----------+
| Implementation                                                                      | Status                     | Reporter  |
+=====================================================================================+============================+===========+
| `CPython 2.3+ <http://www.python.org/>`_                                            | Works                      | ashcrow   |
+-------------------------------------------------------------------------------------+----------------------------+-----------+
| `CPython 3.0 <http://www.python.org/>`_                                             | Works in Python3.0 branch  | ashcrow   |
+-------------------------------------------------------------------------------------+----------------------------+-----------+
| `Stackless 2.3+ <http://www.stackless.com/>`_                                       | Untested                   | ashcrow   |
+-------------------------------------------------------------------------------------+----------------------------+-----------+
| `Jython 2.5 <http://www.jython.org/>`_                                              | Works                      | ashcrow   |
+-------------------------------------------------------------------------------------+----------------------------+-----------+
| `IronPython 2.0 <http://www.codeplex.com/Wiki/View.aspx?ProjectName=IronPython/>`_  | Untested                   | ashcrow   |
+-------------------------------------------------------------------------------------+----------------------------+-----------+
| `IronPython 1.x <http://www.codeplex.com/Wiki/View.aspx?ProjectName=IronPython/>`_  | Broken                     | ashcrow   |
+-------------------------------------------------------------------------------------+----------------------------+-----------+
| `Pypy <http://codespeak.net/pypy/dist/pypy/doc/home.html/>`_                        | Works                      | fijal     |
+-------------------------------------------------------------------------------------+----------------------------+-----------+


Optional Tools
--------------
 #. `rpm-build <http://www.rpm.org/max-rpm-snapshot/rpmbuild.8.html>`_ - Should be packaged in your RPM distribution


Source
------
You can clone the repo over http via :program:`git` through the following command:::

   $ git clone http://git.fedorahosted.org/git/director.git


Style
-----
:pep:`0008` should be followed. This outlines the highlights that we require above and beyond. Your code must follow this (or note why it can't) before patches will be accepted.

   * Global variables should be in ALLCAPPS
   * attributes should be all lowercase
   * classes should be CamelCased? ... filenames should be lowercase.
   * functions and methods should be lowercase with spaces replaced with _'s::

          def a_test_method(self):
              pass

   * classes should subclass object unless it subclasses a different object::

          class Person(object):
              pass

          class Steve(Person):
              pass

   * 4 spaces per indent level
   * max length is 79 chars.
   * Single quotes preferred over double quotes.
   * avoid from x import * imports unless a must use
   * modules, functions, classes, and methods all must have docstrings - doc strings should be descriptive of what objects, functions, and methods do
   * document any potentially confusing sections of code
   * functions and methods should be broken down in such a way as to be easily understood and self contained
   * use descriptive variable names, only use things like x, y, etc.. when doing integer loops and even then see if you can use more descriptive names
   * Pull the interpreter from the environment like so:::

      #!/usr/bin/env python

   * main should use the standard main structure like:::

      if __name__ == '__main__':
          # Code goes here


Git
---

Branching
`````````
<<<<<<< HEAD:docs/development.rst
The best way to develop on Director is to branch feature sets. For instance, if you were to add xml deserialization you would want to branch locally and work on that branch.::
=======
The best way to develop on director is to branch feature sets. For instance, if you were to add xml deserialization you would want to branch locally and work on that branch.::
>>>>>>> Merged 1.2.0 branch.:docs/development.rst

   $  git branch
   * master
   $ git status
   # On branch master
   nothing to commit (working directory clean)
   $ git branch xmldeserialization
   $ git checkout xmldeserialization

Now we pretend you are all finished and have done at least one commit to the xmldeserialization branch.::


   $ git-format-patch master
   0001-created-initial-classes.patch
   0002-added-in-documentation.patch
   $


You now have patch sets which you can send in for perusal and acceptance. You can submit them via email. If you are interested in working directly on the project then submitting a few patches is the place to start. If, for some reason, you are unable to attach patches to the ticket system you can email the patches to 

the user smilner+director at the domain red hat dot(.) com.


Running Unit Tests
``````````````````


Running the test suite is as simple as running :command:`setup.py test`. The results look like:::

   $ ./setup.py test
   <snip>
   Ran 12 tests in 0.049s

   OK
   $ 
