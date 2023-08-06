# -*- coding: utf-8 -*-
"""Recipe z2testrunner"""

import os
import zc.recipe.egg
from zc.buildout import easy_install


class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        python = options.get('python', buildout['buildout']['python'])
        options['executable'] = buildout[python]['executable']
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options.setdefault('eggs', 'zc.recipe.egg')

        self.zcegg = zc.recipe.egg.Egg(buildout, options['recipe'], options)

    def install(self):
        """installer"""

        options = self.options
        reqs, ws = self.zcegg.working_set([options['recipe']])

        packages = [x for x in options.get('packages', '').split('\n')
                    if x]
        modules = [x for x in options.get('modules', '').split('\n')
                   if x]
        extrapaths = [x for x in options.get('extra-paths', '').split('\n')
                   if x]
        scr = os.path.join(options['bin-directory'], options['zope2part'])

        exitwithstatus = options.get('exit-with-status', False)
        if exitwithstatus == 'true':
            exitwithstatus = True

        return easy_install.scripts(
            [(self.name, options['recipe']+'.ctl', 'run')],
            ws,
            options['executable'],
            options['bin-directory'],
            arguments = [scr, packages, modules, extrapaths, exitwithstatus],
            )

    def update(self):
        """updater"""
        self.install()
