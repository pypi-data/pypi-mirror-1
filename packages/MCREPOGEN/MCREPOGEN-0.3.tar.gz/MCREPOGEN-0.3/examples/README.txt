==================
MCREPOGEN Examples
==================

The configuration files included in this directory are meant to give examples
of the different types of features that MCREPOGEN-generated repositories can
have.

To see the effect that these different configurations have on the generated
trees,  the easiest way is to run

::

  gen_random_history -f <example_configuration> -o example.fi

And then import the fast-import file into the VCS of your choice for
exploration.  For example, using Bazaar and the bzr-fastimport plugin one
could do

::

  $ bzr init example
  $ cd example
  $ bzr fast-import ../example.fi
  $ bzr log -v # etc...

