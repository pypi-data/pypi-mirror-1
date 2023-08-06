===========================
The tl.testing distribution
===========================

This package provides various utilities that can be used when writing tests.


Sandboxes of directories and files
==================================

When testing code that modifies directories and files, it is useful to be able
to create and inspect a sample tree of directories and files easily. The
``tl.testing.fs`` module provides support for creating a tree from a textual
description, listing it in the same format and clean up after itself.

In a doc test, these facilities might be used like this to create and list a
directory, a file and a symbolic link:

>>> from tl.testing.fs import new_sandbox, ls
>>> new_sandbox("""\
... d foo
... f foo/bar asdf
... l baz -> foo/bar
... """)

>>> ls()
l baz -> foo/bar
d foo
f foo/bar asdf

See the file ``fs.txt`` found with the source code for further advice,
including how to set up and tear down tests using file-system sandboxes.


Installing callable scripts
===========================

Some functionality one might want to test makes use of external programs such
as a pager or a text editor. The ``tl.testing.script`` module provides
utilities that install simple mock scripts in places where the code to be
tested will find them. They take a string of Python code and create a wrapper
script that sets the Python path to match that of the test and runs the code.

This is how such a mock script might be used in a doc test:

>>> from tl.testing.script import install
>>> script_path = install("print 'A simple script.'")
>>> print open(script_path).read()
#!...
<BLANKLINE>
import sys
sys.path[:] = [...]
<BLANKLINE>
print 'A simple script.'

>>> import subprocess
>>> sub = subprocess.Popen(script_path, shell=True, stdout=subprocess.PIPE)
>>> stdout, stderr = sub.communicate()
>>> print stdout
A simple script.

See the file ``script.txt`` found with the source code for further
possibilities how to install and access mock scripts as well as how to tear
down tests using mock scripts.


Doc-testing the graphical content of cairo surfaces
===================================================

While it is straight-forward to compare the content of two `cairo`_ surfaces
in Python code, handling graphics is beyond doc tests. However, the `manuel`_
package can be used to extract more general test cases from a text document
while allowing to mix them with doc tests in a natural way.

.. _cairo: http://cairographics.org/pycairo/

.. _manuel: http://pypi.python.org/pypi/manuel

The ``tl.testing.cairo`` module provides a test suite factory that uses manuel
to execute graphical tests formulated as restructured-text figures. The
caption of such a figure is supposed to be a literal Python expression whose
value is a cairo surface, and its image is used as the test expectation.

This is how a surface might be compared to an expected image in a doc test:

::

    >>> import cairo
    >>> from pkg_resources import resource_filename

    >>> holmenkollen = resource_filename(
    ...     'tl.testing', 'testimages/holmenkollen.png')

    .. figure:: tl/testing/testimages/holmenkollen.png

        ``cairo.ImageSurface.create_from_png(holmenkollen)``

See the file ``cairo.txt`` found with the source code for further advice and
documentation of the possible test output.


Change log
==========

For a continuously updated change log, see
<https://svn.thomas-lotze.de/repos/public/tl.testing/trunk/CHANGES.txt>.


Contact
=======

This package is written by Thomas Lotze. Please contact the author at
<thomas@thomas-lotze.de> to provide feedback, suggestions, or contributions.

See also <http://www.thomas-lotze.de/en/software/>.


.. Local Variables:
.. mode: rst
.. End:
