Introduction
============

`buildout.extensionscripts` is a convenient way to shoot yourself in the foot
and provides more than enough rope to hang yourself.

With that out of the way, we can look what it can be used for.

To use `buildout.extensionscripts`, you add it as an extension in a buildout
like this::

  [buildout]
  extensions = buildout.extensionscripts

After that you can add one or more lines like the following to the `buildout`
section::

  extension-scripts =
      ${buildout:directory}/somescript.py:callable_name

When you do that, you got an easy way to write a buildout extensions without
the need of an egg. The `callable_name` in `somescript.py` will be called
with one argument which is the dictionary like buildout config.

Now have fun shooting and or hanging yourself by changing that.
