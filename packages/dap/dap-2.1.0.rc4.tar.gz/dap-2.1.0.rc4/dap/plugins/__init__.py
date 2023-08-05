import os
import re
import logging

from pkg_resources import working_set

from dap.exceptions import ExtensionNotSupportedError


def loadplugins():
    plugins = []

    for k, v in working_set.by_key.items():
        pluginSection = v.get_entry_map().get('dap.plugin', None)
        if pluginSection:
            for ep in pluginSection.values():
                plugins.append(ep.load())

    return plugins


def loadhandler(file_, environ=None, plugins=None):
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
            return plugin.Handler(file_, environ)

    raise ExtensionNotSupportedError, 'No handler available for file %s.' % file_
