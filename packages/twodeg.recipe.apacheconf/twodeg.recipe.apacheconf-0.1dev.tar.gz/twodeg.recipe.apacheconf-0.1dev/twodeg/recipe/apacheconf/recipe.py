# -*- coding: utf-8 -*-
"""Recipe apacheconf"""
import os.path
from z3c.recipe.filetemplate import FileTemplate
from zc.recipe.egg import Egg

class Recipe(FileTemplate):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.egg = Egg(buildout, options['recipe'], options)

    def install(self, update=True):
        """Installer, simply adds the working set to the python_path option"""
        
        base_dir = self.buildout['buildout']['directory']
        sys_path = ""
        requirements, ws = self.egg.working_set()
        ws_locations = [d.location for d in ws]

        extra_paths = ws_locations
        extra_paths.extend(self.egg.extra_paths)
        python_path = ", ".join(["'%s'" % ep for ep in extra_paths])
        if self.options.get('sys_path', 'false').lower() == 'true':
            sys_path = " + sys.path"
        self.options['python_path'] = '"[ %s ]%s"' % (python_path, sys_path)
        return super(Recipe, self).install(update)
