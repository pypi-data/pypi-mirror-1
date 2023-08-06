# -*- coding: utf-8 -*-
"""Recipe env"""

import os

class Recipe(object):
    """zc.buildout recipe that reflects the current OS environment variables
    into its options.
    """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        options.update(os.environ)
        options['UID'] = str(os.getuid())
        options['GID'] = str(os.getgid())

    def install(self):
        """Installer"""
        return tuple()

    def update(self):
        """Updater"""
        pass

