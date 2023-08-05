"""Plugins for accessing data formats.

This module contains plugins for accessing different data formats,
together with functions to locate and load the proper handlers.
"""
import os
import re

from pkg_resources import iter_entry_points

from dap.exceptions import ExtensionNotSupportedError


def loadplugins(throw_errors=False):
    """Load all available plugins.

    This function returns a list of all available plugins as modules.
    """
    plugins = []
    for entrypoint in iter_entry_points("dap.plugin"):
        try:
            plugins.append(entrypoint.load())
        except ImportError:
            if throw_errors: raise
    return plugins


def loadhandler(file_, environ=None, plugins=None):
    """Load a handler for a given file.

    This function returns a Handler object able to process a given data
    file. Eg:

        >>> H = loadhandler('file.nc')  # load a netCDF file
        >>> dataset = H._parsecontraints()

    This will load the full (unconstrained) dataset to ``dataset``.
    """
    if environ is None: environ = os.environ.copy()

    if plugins is None:
        plugins = loadplugins(throw_errors=environ.get('x-wsgiorg.throw_errors', False))

    # Check each plugin to see which one handles this file.
    for plugin in plugins:
        p = re.compile(plugin.extensions)
        m = p.match(file_)
        if m:
            try:
                return plugin.Handler(file_, environ)
            except:
                if environ.get('x-wsgiorg.throw_errors'): raise

    raise ExtensionNotSupportedError('No handler available for file %s.' % file_)
