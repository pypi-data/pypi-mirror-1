"""\
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

``absimport()``
    Perform an absolute import and return the imported module

"""

import os
import logging
log = logging.getLogger(__name__)

#
# AttributeDict
#

class AttributeDict(dict):
    def __getattr__(self, name):
        if not self.has_key(name):
            raise AttributeError('No such attribute %r'%name)
        return self.__getitem__(name)

    def __setattr__(self, name, value):
        raise AttributeError(
            'You cannot set attributes of this object directly'
        )

#
# Path Functions
#

# relpath path import (available in Python 2.6 and above)
try:
    import posixpath
    relpath = posixpath.relpath
except (NameError, AttributeError):
    from posixpath import curdir, sep, pardir, join
    def relpath(path, start=curdir):
        """Return a relative version of a path"""
        if not path:
            raise ValueError("no path specified")
        start_list = posixpath.abspath(start).split(sep)
        path_list = posixpath.abspath(path).split(sep)
        # Work out how much of the filepath is shared by start and path.
        i = len(posixpath.commonprefix([start_list, path_list]))
        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return curdir
        return join(*rel_list)
except (ImportError):
    # We are in the wrong platform
    def relpath(path, start=curdir):
        raise NotImplementedError(
            'The relpath() function is only implemented on posix platforms'
        )

def uniform_path(path):
    return os.path.abspath(os.path.normcase(os.path.normpath(path)).replace('\\', '/'))

#
# Import functions
#

class RelativeImportError(Exception):
    pass

_relative_modules = {}

def relimport(module_path, current_module_filename, path_to_package, from_=None):
    log.debug(
        "Requesting module path: %r, "
        "current file: %r, path to package root: %r",
        module_path,
        current_module_filename,
        path_to_package
    )
    if not module_path.startswith('.'):
        raise ValueError('The module path %r is not a relative path'%module_path)
    if not path_to_package.startswith('..'):
        raise ValueError('The path to package %r is not a relative path from the importing file'%path_to_package)
    if '/' in module_path:
        raise ValueError("Shouldn't have a / character in the module path")
    if '\\' in module_path:
        raise ValueError("Shouldn't have a \ character in the module path")

    # Find the module path of the module to import
    up, new_rel_mod_path =  how_many_levels_up(module_path)
    package_directory = dir_containing_package_root(path_to_package, current_module_filename)
    up, current_abs_module_path = module_path_of_current_module(current_module_filename, package_directory, up)
    new_abs_mod_path = abs_mod_path(current_abs_module_path, up, new_rel_mod_path)
    module_to_import, directory_containing_module = adjust_path_for_imp(new_abs_mod_path, package_directory)

    import imp
    try:
        fp, pathname, description = imp.find_module(module_to_import, [directory_containing_module])
    except ImportError:
        log.error('No such module %r import relative to %r'%(module_path, current_module_filename))
        raise RelativeImportError('No such module %r import relative to %r'%(module_path, current_module_filename))
    try:
        mod = imp.load_module(module_to_import, fp, pathname, description)
        _relative_modules[(directory_containing_module, module_to_import)] = mod
    finally:
        # Since we may exit via an exception, close fp explicitly.
        if fp:
            fp.close()
    return handle_from_clause(mod, from_)

def handle_from_clause(module, from_):
    """\
    Takes care of parsing the ``from_`` string and finding the objects in
    ``module``. If one object is imported it is returned, otherwise a tuple of the
    requested objects is returned.
    """
    if from_ is None:
        return module
    results = []
    for name in from_.split(','):
        name = name.strip()
        if not hasattr(module, name):
            raise ImportError('cannot import name %s'%name)
        results.append(getattr(module, name))
    if len(results) == 1:
        return results[0]
    return tuple(results)

def how_many_levels_up(module_path):
    """\
    Calculates how many directories up the relative import starts and returns:

    * the number of directories up as an integer
    * the module path from the directory where the import starts
    """
    up = 0
    rel_module_path = module_path
    while rel_module_path.startswith('.'):
        up += 1
        rel_module_path = rel_module_path[1:]
    log.debug("Want to import %r, %r up from current module", rel_module_path, up)
    return up, rel_module_path

def dir_containing_package_root(path_to_package, current_module_filename):
    """\
    Returns the directory path containing the package's top ``__init__.py``
    file based on the value provided for the path to the package and the path and
    filename of the module the import is occurring from.
    """
    package_directory = uniform_path(os.path.join(current_module_filename, path_to_package, '../../'))
    log.debug("Package directory: %r", package_directory)
    return package_directory

def module_path_of_current_module(current_module_filename, package_directory, up):
    """\
    Calculate the absoulte module path of the current module and adjust the
    value of the ``up`` variable if the module filename ends with ``__init__.py``
    as the module path should be one lower than other files in the same directory.
    """
    new_up = up
    current_module_path = uniform_path(current_module_filename)[len(package_directory)+1:]
    # Ignore the extension
    current_module_path = '.'.join(current_module_path.split('.')[:-1])
    if current_module_path.endswith('/__init__'):
        current_module_path = current_module_path[:-9]
        new_up -= 1
    current_module_path = current_module_path.replace('/', '.')
    log.debug("Module path of current module: %r", current_module_path)
    return new_up, current_module_path

def abs_mod_path(current_abs_module_path, up, new_rel_mod_path):
    """\
    Calculate the absolute module path of the new import from the absolute module
    path of the current module the number of steps up to where the relatvie path
    begins and the relative module import path from that directory.
    """
    # Get the full module path
    full_mod_path = current_abs_module_path
    if up:
        parts = full_mod_path.split('.')
        parts = parts[:-up]
        full_mod_path = '.'.join(parts)
    if full_mod_path:
        full_mod_path = full_mod_path + '.' + new_rel_mod_path
    else:
        full_mod_path = new_rel_mod_path
    log.debug("New abs module path: %r", full_mod_path)
    return full_mod_path

def adjust_path_for_imp(new_abs_mod_path, package_directory):
    """\
    Adjust the path so that imp doesn't need to deal with sub-modules
    """
    end_mod_path = new_abs_mod_path
    directory = package_directory
    parts = end_mod_path.split('.')
    for part in parts[:-1]:
        directory += '/'+part
    end_mod_path = parts[-1]
    log.debug("Importing %r from %r", end_mod_path, directory)
    return end_mod_path, directory

def absimport(mod_path, from_=None):
    """\
    Perform an absolute import of ``mod_path`` and return the last module
    """
    if from_ == '':
        raise Exception("The from_ argument cannot be ''")
    mod = __import__(mod_path)
    parts = mod_path.split('.')
    so_far = parts[0]
    for part in parts[1:]:
        so_far+='.'+part
        if not hasattr(mod, part):
            raise ImportError('No such module or object %r'%(so_far,))
        mod = getattr(mod, part)
    return handle_from_clause(mod, from_)

