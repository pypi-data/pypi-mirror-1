# -*- coding: utf-8 -*-
"""Recipe recipe"""

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here
        
        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        f = open('/tmp/test.txt', 'w')
        f.write('my.demo.recipe was here')
        f.close()
        return tuple()

    def update(self):
        """Updater"""
        f = open('/tmp/test.txt', 'a')
        f.write('my.demo.recipe was updated')
        f.close()



