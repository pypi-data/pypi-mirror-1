# -*- coding: utf-8 -*-
"""Recipe linktally"""

import logging
import os
import string
import sys

LINKTALLY_VERSION = '0.1.0'
VERSION = LINKTALLY_VERSION + '-3'

SDIST_LOC = 'http://plone.org/products/linktally/releases/%s/' \
            'linktally-%s.tar.gz' % (LINKTALLY_VERSION, LINKTALLY_VERSION)
EXTRA_EGGS = '''
linktally == %s
collective.recipe.linktally
pysqlite == 2.4.0
''' % LINKTALLY_VERSION

PRODUCTS = ['']

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        self.logger = logging.getLogger(self.name)

        location = os.path.join(buildout["buildout"]["parts-directory"],
                                self.name)
        self.options['location'] = location
        if not self.options.has_key('config'):
            self.options['config'] = os.path.join(location, 'linktally.conf')

        eggs = self.options.get('eggs', '')
        existing_egg_names = [x.split()[0]
                              for x in eggs.split('\n') if x.strip()]
        for egg in EXTRA_EGGS.split('\n'):
            if not egg.strip():
                continue
            egg_name = egg.split()[0]
            if egg_name not in existing_egg_names:
                eggs += '\n' + egg

        self.options['eggs'] = eggs
        self.options['products'] = self.extracted_dir
        self.options['executable'] = self.name

        self.distros = self.distros_recipe(buildout, name, options)
        self.eggs = self.eggs_recipe(buildout, name, options)
        self.scripts = self.scripts_recipe(buildout, name, options)

    @property
    def extracted_dir(self):
        return os.path.join(self.options['location'],
                            'linktally-%s' % LINKTALLY_VERSION)

    def distros_recipe(self, buildout, name, options):
        import plone.recipe.distros
        return plone.recipe.distros.Recipe(buildout, name, options)

    def eggs_recipe(self, buildout, name, options):
        import zc.recipe.egg
        return zc.recipe.egg.Eggs(buildout, name, options)

    def scripts_recipe(self, buildout, name, options):
        import zc.recipe.egg
        return zc.recipe.egg.Scripts(buildout, name, options)

    def install(self):
        """Do recipe work"""

        self.options['urls'] = SDIST_LOC
        self.options['find-links'] = 'file://' + self.extracted_dir
        self.options['scripts'] = 'tallylinks'
        self.options['entry-points'] = \
            'tallylinks=collective.recipe.linktally.runtally:run'
        self.options['arguments'] = '"' + self.options['config'] + '"'

        self.distros.install()
        self.eggs.install()
        self.scripts.install()

        module = ''
        for x in self.options["recipe"]:
            if x in (':', '>', '<', '='):
                break
            module += x
        whereami = sys.modules[module].__path__[0]
        f = open(os.path.join(whereami, 'linktally.conf.template'))
        template = f.read()
        f.close()
        template = string.Template(template)

        config = dict(database=self.options.get('database'),
                      logfile=self.options.get('logfile'),
                      linksurl=self.options.get('linksurl'),
                      prefix=self.options.get('linksprefix', ''))
        template = template.safe_substitute(config)

        targetdir = os.path.dirname(self.options['config'])
        if not os.path.exists(targetdir):
            os.makedirs(targetdir)
            self.options.created(targetdir)

        f = open(self.options['config'], 'w')
        f.write(template)
        f.close()

        self.options.created(self.options['config'])

        return self.options.created()

    def update(self):
        """Update recipe work"""
