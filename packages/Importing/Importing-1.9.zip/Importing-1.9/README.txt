Dynamic, Lazy, and Weak Imports with the ``Importing`` Toolkit
==============================================================

Need to import an object when all you've got is its name?  Need to lazily
import modules, such that they don't actually get loaded until you use them?
Want to have some code in a module that only gets run *if* another module is
imported?  Then you need the "Importing" toolkit.

Installing the toolkit (using ``"easy_install Importing"`` or
``"setup.py install"``) allows you to access the ``peak.util.imports`` module.
This module was previously bundled for years inside of the general PEAK
distribution, but is now available as a standalone module for your convenience.

The "Importing" toolkit does not install or use any special import hooks, and
is compatible with zipfile imports, ``py2exe``, etc.  Lazy and weak imports
should be compatible with almost any import hooks or hacks, as long as they
have reasonable support for the ``reload()`` builtin.  The dynamic import
utilities, however, require only that ``__import__()`` work correctly, and so
should work anywhere that normal Python imports work.

.. contents:: **Table of Contents**

You may access any of the following APIs by importing them from
``peak.util.imports``:


Dynamic Imports
---------------

Sometimes you need to get an object based on a name that you don't know until
runtime.  You could kludge something together with ``exec`` or ``__import__``,
but if you need to be able to reference nested classes, class methods, or
other object attributes, and want to handle packages correctly, you will
want to use one of these routines.

All of these routines accept an optional ``globalDict`` parameter to allow
relative importing; see the section on `Relative/Absolute Importing`_ below
for details.

importString(name [, globalDict])
    Import an item specified by a string

    Example Usage::

        attribute1 = importString('some.module:attribute1')
        attribute2 = importString('other.module:nested.attribute2')

    ``importString()`` imports an object from a module, according to an
    import specification string: a dot-delimited path to an object
    in the Python package namespace.  For example, the string
    ``"some.module.attribute"`` is equivalent to the result of
    ``from some.module import attribute``.

    For readability of import strings, it's sometimes helpful to use a ``:`` to
    separate a module name from items it contains.  It's optional, though,
    as ``importString()`` will convert the ``:`` to a ``.`` internally anyway.

importObject(name_or_object [, globalDict])
    Convert a possible string specifier to an object

    If `name_or_object` is a string or unicode object, this routine will import
    it using ``importString()``.  Otherwise, the passed-in object is returned.

    This routine is useful for APIs that want to accept either a (non-string)
    object, or a string designating the object to be used.  They can simply
    call ``importObject()`` on their input without needing to inspect it.

importSequence(string_or_sequence [, globalDict])
    Convert a string or sequence to a list of objects.

    If `string_or_sequence` is a string or unicode object, it is treated as a
    comma-separated list of names to import using ``importString()``, and a
    list of imported objects is returned.  (Whitespace around the commas is
    permitted.)

    If `string_or_sequence` is not a string but is iterable, this returns a
    list created by calling ``importObject()`` on each element of the sequence.

importSuite(name_or_sequence [, globalDict])
    Convert a string or sequence to a ``unittest.TestSuite``

    This routine is identical to ``importSequence()`` except that a
    ``unittest.TestSuite`` is returned instead of a list.


Relative/Absolute Importing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

All of the above routines take an optional ``globalDict`` second argument in
order to support imports relative to a given package (in which case the
passed-in ``globalDict`` should be a module dictionary in the desired package).
These routines do *not* support Python 2.5 relative import syntax.  All imports
done by these routines are absolute, unless you specify a ``globalDict`` (in
which case they are relative to the module the ``globalDict`` came from,
falling back to absolute if there is no relative match).


Lazy Imports
------------

Sometimes you may want to import a module that isn't needed right away.  A
common solution is to put the import inside of a function, so that it doesn't
occur until the function is called.  However, this is slow, increases startup
time, and it can be a bit harder to tell what's going on.  So the Importing
toolkit provides a way to access a module lazily, such that it can be
"imported" in top level code, but not actually *loaded* until the module is
used in some way.  (And unlike many other lazy importing tools for Python,
this API can be applied to *any* Python module and does not interfere
with normal imports of the targeted module(s), whether they are lazily loaded
before or after the normal imports.)

lazyModule(moduleName)
    Return module `moduleName`, but with its contents loaded "on demand"

    This function returns ``sys.modules[moduleName]``, if present.  Otherwise
    it creates a ``LazyModule`` object for the specified module, caches it
    in 'sys.modules', and returns it.

    ``LazyModule`` is a subclass of the standard Python "module" type, that
    remains empty until an attempt is made to access one of its attributes.
    At that moment, the module is loaded into memory, and any hooks that were
    defined via ``whenImported()`` (See the `"Weak" Imports`_ section below)
    are invoked.

    Note that calling ``lazyModule()`` with the name of a non-existent or
    unimportable module will delay the ``ImportError`` until the moment that
    an access is attempted.  The ``ImportError`` will be repeated *every time*
    an attribute access is attempted on the broken module, until the problem is
    corrected.

    Example usage::

        sdist = lazyModule('distutils.commands.sdist')

    This is roughly equivalent to ``import distutils.commands.sdist as sdist``,
    except that the real import doesn't take place until/unless you try to
    access some attribute of the ``sdist`` object -- unless of course the
    module was already imported before the above line was executed.


"Weak" Imports
--------------

Sometimes you have code in a module that's only needed to support some
third-party module, that your user(s) may or may not be using.  A common
approach to solving this problem is to try importing the third-party module,
but this may import it unnecessarily, if the program never ends up actually
using the module.

So the Importing toolkit offers a solution by combining lazy module loading
with the ability to have a callback run whenever a named module is actually
used.  The registered callback can be used to import additional support code,
register adapters or services or generic functions, or do whatever else might
be needed to add support when the optional third-party module is imported.  But
the callback will be invoked only as soon as the third-party module is *used*
(i.e. any of its attributes are accessed), and not a moment before.

whenImported(moduleName, callback)
    Call ``callback(module)`` when module named `moduleName` is first used

    `callback` must accept one argument: the module object named by
    `moduleName`.  `moduleName` must be a fully qualified (i.e. absolute)
    module name.  The callback **must not allow any unhandled exceptions to
    escape**, or it may prevent other registered callbacks from running.

    If the named module has already been loaded, ``callback(module)`` is
    called immediately, and the module object is returned from this function.

    If the module has not been imported, or has only been imported lazily,
    then the callback is invoked when the module is first *used*, and a lazy
    import of the module is returned from this function.

    If the module was imported lazily and used before calling this function,
    the hook is called immediately, and the loaded module is returned from this
    function.

    Note that using this function implies a possible lazy import of the
    specified module, and lazy importing means that any 'ImportError' will be
    deferred until the module is used.


Deprecated Features
-------------------

For backward-compatibility with PEAK's experimental "module inheritance"
feature, ``peak.util.imports`` has some limited support for logical module
paths, in the ``joinPath()`` function and the optional ``relativePath``
argument to ``lazyModule()``.  There is also a ``getModuleHooks()`` function
that is used by the "module inheritance" system.

Please do not use any of these API features, as I would like to remove them or
make them private as soon as the "module inheritance" feature is removed from
PEAK proper.


Mailing List
------------

Please direct questions regarding this package to the PEAK mailing list; see
http://www.eby-sarna.com/mailman/listinfo/PEAK/ for details.
