==========
extensions
==========

`extensions` is a simple plugin system inspired from setuptools entry points
[#ep]_. It allows an application to define and/or use plugins.

How to define a plugin
======================

A plugin can be any callable object . It has to be registered through the
`extensions` registry.

For example, let's take a simple function that calculates the average of
some numbers, and let's save it into a file called `extensions.py` in a
package called `myapp`::

    def average(*args):
         return sum(*args) / len(args)

This function can be registered in the plugin system using the `register`
function. Plugins have a **name** and belong to a **group**. For our
example, the group can be `myapp.operator` and the name `average`::

    from extensions import register

    register('myapp.operator', 'average', 'myapp.extensions:average')

Notice that the group name includes the name of the package, which is a good
practice to avoid collisions since the group names are global to all applications
that uses `extensions`.

How to use a plugin
===================

Iterate over registered plugins
:::::::::::::::::::::::::::::::

`extensions` provides a `get` function that allows you to iterate over all
registered plugins for a given group::

    from extensions import get

    for plugin in get(group='myapp.operator'):
        print plugin.name

You can also give the `name` to the function::

    for plugin in get(group='myapp.operator', name='average'):
         print plugin.name

Or even iterate over **all** plugins::

    from itertools import islice

    for plugin in islice(get(), 5):
        print plugin.name

The Plugin object
:::::::::::::::::

The objects returned by the `get` function are `Plugin` class instances.

The `Plugin` class provides one method called `load`, that returns
the registered object, so you can use it ::

    # let's get the plugin `average` of the group `myapp.operator`
    plugin = get(group='myapp.operator', name='average').next()

    # let's load it
    func = plugin.load()

    # let's use it now
    average = func(1, 2, 3)

Plugin also provides a `name` and a `group` attribute, that corresponds
to the `name` of the registered plugin, and to its `group`.

Distribute your plugins
=======================

If you want to distribute your plugins, you just have to import the module
that registers the plugins into your `setup.py` file::

    from distutils.core import setup
    from myapp import plugins  # registers the plugins

    setup(name='myapp', version='1.0'
          packages=['myapp'])

This will register the plugins when the package is installed by creating
a special file called `PLUGINS` into the `.egg-info` directory created when
your package is installed.

Compatibility with setuptools entry points
==========================================

`extensions` is fully compatible with setuptools entry points. So you can iterate 
and use entry points defined in third-party applications that are installed 
in your Python.

References
==========

.. [#ep]
   http://peak.telecommunity.com/DevCenter/setuptools#extensible-applications-and-frameworks

