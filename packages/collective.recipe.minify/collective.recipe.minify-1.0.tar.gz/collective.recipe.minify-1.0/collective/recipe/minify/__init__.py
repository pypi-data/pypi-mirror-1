# -*- coding: utf-8 -*-
"""Recipe minify"""

import zc.buildout
import zc.recipe.egg

from collective.recipe.minify.runner import minify
TRUE_VALUES = ('yes', 'true', '1', 'on')

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name = buildout, name

        self.commands = {
            '.css': options.get('css-command', ''),
            '.js': options.get('js-command', ''),
            }
        self.ignore = [pat for pat in options.get('ignore', '').split()]
        self.paths = [path.strip() for path in options.get('paths', '').split()]

        if options.get('include-devel', 'false').lower() in TRUE_VALUES:
            self.paths.extend([path.strip() for path in
                               self.buildout['buildout']['develop'].split()])

        if not self.paths:
            raise ValueError('No paths specified!')

        options.setdefault('suffix', '-full')
        options.setdefault('verbose', 'false')

        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)

        self.options = options

    def install(self):
        """Installer"""
        buildout = self.buildout['buildout']
        initialization_template = """
import logging
loglevel = logging.%(loglevel)s
# Allow the user to make the script more quiet (say in a cronjob):
if sys.argv[-1] in ('-q', '--quiet'):
    loglevel = logging.WARN
logging.basicConfig(level=loglevel,
    format='%%(levelname)s: %%(message)s')

commands = %(commands)s
paths = %(paths)s
ignore = %(ignore)s
suffix = "%(suffix)s"
        """
        opts = self.options.copy()
        opts['commands'] = self.commands
        opts['ignore'] = self.ignore
        opts['paths'] = self.paths

        if self.options.get('verbose', 'false') in TRUE_VALUES:
            opts['loglevel'] = 'DEBUG'
        else:
            opts['loglevel'] = 'INFO'

        initialization = initialization_template % opts
        requirements, ws = self.egg.working_set(['collective.recipe.minify',
                                                 'zc.buildout',
                                                 'zc.recipe.egg'])

        return zc.buildout.easy_install.scripts(
                [(self.name, 'collective.recipe.minify.runner', 'minify')],
                ws, buildout['executable'], buildout['bin-directory'],
                arguments=('commands, paths, ignore, suffix'),
                initialization=initialization)

    def update(self):
        """Updater"""
        pass
