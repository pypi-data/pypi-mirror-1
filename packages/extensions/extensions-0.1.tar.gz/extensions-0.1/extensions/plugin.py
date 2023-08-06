# -*- coding: utf8 -*-
""" Plugin class
"""

class Plugin(object):
    """Plugin class"""
    def __init__(self, ep, group, name):
        self._ep = ep
        self.name = name
        self.group = group

    def load(self):
        """Loads the registered object and returns it."""
        return self._ep.load()

