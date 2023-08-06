===============
tl.buildout_gtk
===============

A `zc.buildout`_ recipe for installing pygtk, including pygobject and pycairo.

This recipe concerns itself with the Python bindings to the GTK+ library and
its dependencies, GObject and Cairo. It assumes that the C libraries are
available on the system already, along with their header files.

This recipe appears to be reliable, but the feature set is basically
determined by the author's immediate needs. Don't hesitate to send questions,
bug reports, suggestions, or patches to <thomas@thomas-lotze.de>.


Options
=======

Configuration options:
    :pycairo-url:
        URL of the pycairo source code archive to be built.

    :pycairo-md5sum:
        MD5 checksum of the pycairo source code archive.

    :pygobject-url:
        URL of the pygobject source code archive to be built.

    :pygobject-md5sum:
        MD5 checksum of the pygobject source code archive.

    :pygtk-url:
        URL of the pygtk source code archive to be built.

    :pygtk-md5sum:
        MD5 checksum of the pygtk source code archive.

    The default values of these options correspond to the latest project
    versions at the time the recipe was released.

Exported options:
    :location:
        Location of the buildout part containing the compiled Python bindings.

    :path:
        Filesystem path to be added to the Python path in order for the
        bindings to be importable. This may be included in a zc.recipe.egg
        part's ``extra-paths`` option, for example.


Background
==========

There are two reasons for the existence of this recipe: setting up the build
environment for pygtk & friends, and tying together the build instructions of
the related projects for convenience.

The pygtk, pygobject and pycairo projects are built using a standard
configure/make/make install procedure. Unfortunately, they don't offer a
configure option for specifying which Python installation to use, but attempt
to install into the site packages path of the first ``python`` executable
found on the system's binary search path. This recipe has to set up a fake
executable and corresponding ``PATH`` variable for the build processes.


.. _`zc.buildout`: http://www.zope.org/DevHome/Buildout/


.. Local Variables:
.. mode: rst
.. End:
