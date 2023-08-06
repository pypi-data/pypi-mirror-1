=============================================
MCREPOGEN - Markov Chain Repository Generator
=============================================

MCREPOGEN is a generator of random version control histories.  It has a
significant number of parameters that allow one to control the properties
of the repositories that it generates.  It is intended to be used as a
performance testing tool for version control systems.

Installation
============

MCREPOGEN depends on the Bazaar version control system.  Specifically,
you need to have three packages:

  1. Bazaar (http://bazaar-vcs.org)
  2. the bzr-fastimport plugin (https://launchpad.net/bzr-fastimport)
  3. Numpy (http://numpy.scipy.org)

If these three packages are installed, then you should be able to install
MCREPOGEN using::

  python setup.py install


Usage
=====

MCREPOGEN simulates the time evolution of a directory tree and outputs the
resulting history in the fast-export format
(http://www.kernel.org/pub/software/scm/git/docs/git-fast-import.html).  The
main script is ``gen_random_history.py``.  For example::

  gen_random_history.py -r 100 -o test_history.fi

should produce a history of 100 revisions in the file ``test_history.fi``.

Options
-------

`-r`, `--revisions` 
  This controls how many revisions will be created.  The default value is 100.

`-o`, `--output`
  This can be given to specify a filename for the output.  If it is absent,
  the output is sent to the standard output.

Configuration
-------------

Configuration of the parameters of the time evolution is planned, but
currently the only way to change the parameters is to change them directly
in the source code.  All of the classes that act on the directory tree
take a `parameters` dictionary.  To see the possible parameters that can
be specified for a particular class, inspect the `default_parameters` 
attribute.


Theory
======

MCREPOGEN simulates a trajectory of a Markov chain whose states are directory
trees.  Abstractly, a directory tree is a rooted tree with two types of labeled
nodes: file nodes and directory nodes.  The label is the name of the file or
directory.  Each file node has a text associated with it and has no children. 

In this abstract framework, changing the connectivity of a node
corresponds to a "move", changing the text of a file node is an "edit",
eliminating a node is a "deletion" and changing the label of a node is a
"rename".  Note that this framework distinguishes moves and renames
(that is, nodes have a unique identity apart from their label).

The parameters of the generator are the probabilities of the various
types of tree changes in the previous paragraph.

Directory Trees
---------------

In an effort to be VCS agnostic, MCREPOGEN implements a very abstract
interface to a directory tree and to a history of directory trees,
called a branch.  The abstract interface is in `treebranch.py` and those
wishing to use MCREPOGEN on top of another VCS need only implement
that abstract interface, which includes the following methods

* Branch
    - checkpoint
    - get_checkpoint
    - serialize
* Tree
    - id2path
    - path2id
    - iter_files
    - iter_subdirs
    - iter_all_files
    - iter_all_subdirs
    - add_file
    - add_directory
    - remove_file
    - remove_directory
    - move
    - open_file
    - open_file_by_id

See the docstrings in `treebranch.py` for specifications of the behavior
of these methods.  A reference implementation using Bazaar as the underlying
branch and tree objects is in `bzrtreebranch.py`.

Mutators
--------

The transitions in the Markov Chain are implemented by subclasses of the
`Mutator` class which act on a directory tree to change it.  They have a
`mutate` method which takes a directory tree as an argument.  That
method returns the directory tree after it has been affected by the type
of change that is implemented.  A trivial example would be the following
destructive mutator::

  class DeleteAllFiles(Mutator):

      def mutate(self, input_tree):
          for filename in input_tree.iter_all_files():
              input_tree.remove_file(filename)
          return input_tree

Note that although the `mutate` method returns the new directory tree, it
may make those changes by changing the input tree directly.  The `mutate`
method may have side effect on its argument.

A default set of Mutators is provided that implements the basic
tree manipulations that are possible

* FileCreator
* DirectoryCreator
* FileRemover
* FileMover
* DirectoryRemover
* DirectoryMover

The probabilistic model used by each class is described in its
docstring.

Editors
-------

Changing the contents of files is a special type of transition that
doesn't affect the tree structure.  These are implemented by subclasses
of `Editor` (which is itself a subclass of `Mutator`) that implement an
`edit` method.  Similar to a mutator, it takes an input tree as an
argument and returns the changed tree, while not necessarily preserving
its input.  Here is an example of a very intrusive `Editor`::

  class AddTagline(Editor):

      def edit(self, input_tree):
          for filename in input_tree.iter_all_files():
              f_open = input_tree.open_file(filename, 'a')
              f_open.write("This file has been tagged\n")
              f_open.close()
          return input_tree

which appends a tag line to the end of every file in the tree.

The only probabilistic model implemented currently is the generation of
a random patch.  This chooses a random number of hunks and then makes a
random change to each of those hunks.  It is possible to implement
different types of `Editor`s to represent different kinds of textual
changes:  TypoFixer, Refactoring, Appending, etc.

TransitionKernel
----------------

The particular markov chain being simulated is specified by a
`TransitionKernel` which holds a list of mutator instances and a list of
editor instances.  The `step` method takes a directory tree as input and
returns the next state in the markov chain starting from that point.  It
gets there by applying the mutators in order and then the editors.  It
is possible to specify multiple instances of a mutator or editor, but in
many cases this is equivalent to a single instance of the mutator or
editor with different parameter values.
 
