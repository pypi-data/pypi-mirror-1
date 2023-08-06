# -*- coding: utf8 -*-
""" Plugin registry.
"""
from collections import defaultdict

_plugins = defaultdict(list)

def register(group, name, value):
    """Registers a plugin, given a group, name and value."""
    if (name, value) not in _plugins[group]:
        _plugins[group].append((name, value))

def get_registered():
    """Returns registered plugins."""
    return _plugins.items()

def stream_registered():
    """Returns registered plugins as config-like string."""
    entries = []
    for group, group_entries in get_registered():
        entries.append('[%s]' % group)
        for name, value in group_entries:
            entries.append('%s = %s' % (name, value))
        entries.append('')
    if entries == []:
        return ''
    return '\n'.join(entries)

