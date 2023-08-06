BareNecessities Manual
++++++++++++++++++++++

BareNeccessities contains functions and classes I use so frequently I wish
they were in the standard library (in fact one of them is as of Python 2.6!).

These all work with Python 2.4 and above and may work with earlier versions
too.

``AttributeDict``
    This is a dictionary which allows read access to the keys via attributes
    but raises an error if you try to set an attribute.

``relpath()``
    A function to calculate the relative path between two locations (only
    works on POSIX systems)

``uniform_path()``
    Returns an absolute normalised path with any ``\`` characters replaced
    with ``/`` characters

``relimport()``
    Provides a relative import which overcomes a glaring problem with the
    Python 2.5 relative import. This version works in scripts too.

``str_dict()``
    Python 2.x cannot accept dictionaries where the keys are Unicode strings as
    arguments to functions using the ``**`` operator, even if they are only made of
    characters ``a-zA-Z0-9_``. ``str_dict()`` takes such a dictionary with
    Unicode keys and turns the keys into 8-bit strings.

Lets look at each in turn.

The ``AttributeDict`` class
===========================

This is simply a dictionary which allows its keys to be accessed as attributes.
This means that sttribute dictionaries behave a little like JavaScript objects
and is very useful if you want to avoid the use of classes but still want to be
able to group functions together.

Attribute dictionaries cannot have new keys added by attribute assignment to
avoid a user accidentally setting a value which doesn't exist.

Here are some examples:

::

    >>> from bn import AttributeDict
    >>> database = AttributeDict()
    >>> database['connect'] = 'This is just a string, it could be a function'
    >>> print database.connect
    This is just a string, it could be a function
    >>> print database['connect']
    This is just a string, it could be a function
    >>> database.commit = "You can't set new keys as attributes"
    Traceback (most recent call last):
      ...
    AttributeError: You cannot set attributes of this object directly
        

The ``relpath()`` function
==========================

This is an implementation of the Python 2.6 ``os.relpath()`` function but it
only works on POSIX platforms and will work with Python 2.4 and 2.5 as well as
Python 2.6.

``os.path.relpath(path[, start])``

    Return a relative filepath to *path* either from the current directory or
    from an optional *start* point.

Here are some examples. First let's find a directory we know exists:

::

    >>> import os.path
    >>> import bn
    >>> bn_path = '/'.join(os.path.split(bn.__file__)[:-1])

Now let's calculate a relative path (this will work if you are running Python
from the ``test`` directory of the BareNecessities distribution).

::

    >>> from bn import relpath
    >>> relpath(bn_path)
    '../bn'

You can also specify a start path:

::

    >>> doc_dir = os.path.join(bn_path, '../', 'doc')
    >>> relpath(doc_dir, bn_path)
    '../doc'
    
The ``uniform_path()`` function
===============================

When working with paths you often want to know the absolute path with any
``../`` components normalised out and any ``\`` characters converted to ``/``
characters and any cases normailised so that when you compare two different
paths as strings you know you are comparing like with like. The
``uniform_path()`` does this.

::

    >>> from bn import uniform_path
    >>> import os.path
    >>> uniform_path(bn_path) ==  os.path.abspath(os.path.normcase(os.path.normpath(bn_path)).replace('\\', '/'))
    True

The ``absimport()`` function
============================

.. autofunction:: bn.absimport

This function allows you to import a module based on its module path just like
you would in a normal import statement. It is useful because it allows you to
import another module at runtime from within a function or method rather than
when the module is first loaded.

It is similar to the builtin Python ``__import__()`` function apart from two
differences. The ``absimport()`` function:

* returns the module you've imported at the end of the path, not the start so
  ``absimport('path.to.my.module')`` returns the ``module`` module, not the
  ``path`` module

* it takes a ``from_`` argument which allows you to specify a string containing
  the names of objects you want imported from a module

Here are some examples:

::

    >>> from bn import absimport
    >>> absimport('email.utils')
    <module 'email.utils' from ...>
    >>> random, quote = absimport('email.utils', from_='random, quote')
    >>> random, quote
    (<module 'random' from '...'>, <function quote at 0x...>)
    >>> random = absimport('email.utils', from_='random')
    >>> random
    <module 'random' from '...'>


The ``relimport()`` function
============================

Sometimes even the ``absimport()`` function isn't flexible enough. For example,
what if you want to import a module which you know is in a directory two levels
up but you don't know the package name but you have to have the module imported
at load time. In this case you need to use a *relative import*.

Relative imports were introduced into Python 2.5 after the discussion in 
`PEP 328 <http://www.python.org/dev/peps/pep-0328/>`_. They are documented in the
`Intra-package References <http://docs.python.org/tutorial/modules.html#intra-package-references>`_ part
of the Python documentation but they have a severe limitation: if you try to do
a relative import in a package being run as a script the Python uses the
package name ``__main__`` and will not know which package the Python files
really belong to so it won't be able to calculate relative imports and instead
gives up with this error:

::

    ValueError: Attempted relative import in non-package

To get around this we have the ``relimport()`` function which performs a working
relative import in Python 2.4 and above and works in scripts too. The downside
is that the syntax isn't as nice. Here's how it looks:

.. autofunction:: bn.relimport

It can be used like this:

::

    from bn import relimport
    
    absimport = relimport(
        '.',
        __file__,
        '../',
        'absimport',
    )

We can't test this from documentation but the ``bn.relimport_test`` module
contains a relative import to the ``bn`` module so by importing that we can
check it works:

::

    >>> import bn.relimport_test

There are a number of other functions which provide functionality related to
the ``relimport()`` which you can also use if you like.

.. autofunction:: bn.adjust_path_for_imp
.. autofunction:: bn.module_path_of_current_module
.. autofunction:: bn.dir_containing_package_root
.. autofunction:: bn.how_many_levels_up
.. autofunction:: bn.handle_from_clause



The ``str_dict()`` function
===========================

Used like this to convert dictionaries with Unicode keys to ones without so
that they can be used with the ``**`` operator to call functions.

::

    >>> from bn import str_dict
    >>> 
    >>> def test(a, b):
    ...     print a, b
    ...
    >>> test(**{u'a': u'1', u'b': u'2'})
    Traceback (most recent call last):
      File ...
    TypeError: test() keywords must be strings
    >>> test(**str_dict({u'a': u'1', u'b': u'2'}))
    1 2


