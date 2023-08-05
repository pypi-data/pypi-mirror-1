import os
import re
import logging

import dap
from dap.exceptions import ExtensionNotSupportedError


def loadplugins():
    # Discover plugins path.
    path = os.path.join(dap.__path__[0], 'plugins')
    modules = [module[:-3] for module in os.listdir(path) if module.endswith('.py')]

    plugins = []
    for module in modules:
        # Load module
        name = 'dap.plugins.%s' % module
        try:
            module = __import__(name, globals(), locals(), ['*'])
            if hasattr(module, 'extensions'):
                # Store it.
                plugins.append(module)
            else:
                del module
        except ImportError:
            pass

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
