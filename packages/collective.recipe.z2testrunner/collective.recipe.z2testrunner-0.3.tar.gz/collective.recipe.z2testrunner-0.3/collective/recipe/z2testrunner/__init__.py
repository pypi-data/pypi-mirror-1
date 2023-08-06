# -*- coding: utf-8 -*-
"""Recipe z2testrunner"""

import os
import zc.recipe.egg
import zc.buildout.easy_install

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
        exitwithstatus = options.get('exit-with-status', 'false')
        exitwithstatus = exitwithstatus.lower() == 'true'

        initialization = '''import os
'''
        env_section = options.get('environment' , '').strip()
        if env_section:
            env = self.buildout[env_section]
            for key, value in env.items():
                initialization += env_template % (key, value)

        defaults = options.get('defaults', '').strip()
        if defaults:
            defaults = defaults.split()
        else:
            defaults = []

        scr = os.path.join(options['bin-directory'], options['zope2part'])

        return zc.buildout.easy_install.scripts(
            [(self.name, 'collective.recipe.z2testrunner.ctl', 'run')],
            ws,
            options['executable'],
            options['bin-directory'],
            arguments = [scr, defaults, packages, modules, extrapaths, 
                         exitwithstatus],
            initialization=initialization,
            )

    def update(self):
        """updater"""
        self.install()


env_template = """os.environ['%s'] = %r
"""
