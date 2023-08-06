# -*- coding: utf-8 -*-
"""Recipe release"""

import re
import os.path
egg_name_re = re.compile(r'(\S+?)([=<>!].+)')

from getpaid.recipe.release.getpaidcorepackages import GETPAID_PACKAGES
from getpaid.recipe.release.getpaidcorepackages import GETPAID_OTHER_PACKAGES

import zc.recipe.egg


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        findlinks = ['http://getpaid.googlecode.com/files/hurry.workflow-0.9.1-getpaid.tar.gz', \
         'http://getpaid.googlecode.com/files/yoma.batching-0.2.1-getpaid.tar.gz', \
         'http://getpaid.googlecode.com/files/zc.resourcelibrary-0.5-getpaid.tar.gz', \
         'http://getpaid.googlecode.com/files/zc.table-0.5.1-getpaid.tar.gz', \
         'http://download.zope.org/distribution/ssl-for-setuptools-1.10']
        options['find-links'] = "\n%s" % ('\n').join(findlinks)

        # These are passed onto zc.recipe.egg.
        options['eggs'] = self.getpaid_eggs()
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name
            )

    def install(self):
        """Installer"""
        options = self.options
        location = options['location']
        self.egg.install()
        return location
        
    def update(self):
        """Updater"""
        pass

    def getpaid_eggs(self):
        """Read the eggs from dist_plone
        """
        egg_spec = self.options.get('eggs', '')
        explicit_eggs = {}
        for spec in egg_spec.split():
            name = spec
            version = ''
            match = egg_name_re.match(spec)
            if match:
                name = match.groups(1)
                version = match.groups(2)
            explicit_eggs[name] = version
        
        # we get the other packages that people want
        all_packages = []
        addpackages = self.options.get('addpackages', '').split()
        
        for p in addpackages:
            pymodule = GETPAID_OTHER_PACKAGES.get(p, None)
            if pymodule:
                all_packages.append(pymodule)
        
        eggs = []
        for pkg in GETPAID_PACKAGES + all_packages:
            name = pkg.name
            if name in explicit_eggs:
                eggs.append(name + explicit_eggs[name])
                del explicit_eggs[name]
            else:
                if pkg.version is not None:
                    name += "==%s" % pkg.version
                eggs.append(name)
        
        for name, version in explicit_eggs.items():
            eggs.append(name + version)
        
        return '\n'.join(eggs)
