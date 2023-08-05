"""Plugins for accessing data formats.

This module contains plugins for accessing different data formats,
together with functions to locate and load the proper handlers.
"""
import os
import re
import logging

from pkg_resources import working_set

from dap.exceptions import ExtensionNotSupportedError


def loadplugins():
    """Load all available plugins.

    This function returns a list of all available plugins as modules.
    """
    plugins = []

    for k, v in working_set.by_key.items():
        pluginSection = v.get_entry_map().get('dap.plugin', None)
        if pluginSection:
            for ep in pluginSection.values():
                try:
                    plugins.append(ep.load())
                except ImportError:
                    pass

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

    # Add basic logging for the plugin.
    environ.setdefault('logger', logging)
        
    if plugins is None:
        plugins = loadplugins()

    # Check each plugin to see which one handles this file.
    for plugin in plugins:
        p = re.compile(plugin.extensions)
        m = p.match(file_)
        if m:
            try:
                return plugin.Handler(file_, environ)
            except:
                pass

    raise ExtensionNotSupportedError, 'No handler available for file %s.' % file_
