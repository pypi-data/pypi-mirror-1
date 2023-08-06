# -*- coding: utf-8 -*-
"""Recipe zcml"""

import os
import shutil
import re

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

    def install(self):
        """Installer"""
        created = self.build_package_includes()
        return tuple(created)

    update = install

    # from: http://svn.plone.org/svn/collective/buildout/plone.recipe.zope2instance/trunk/src/plone/recipe/zope2instance/__init__.py
    #       revision 66164
    # Modified:
    #  - modified that it returns the pathes created.
    #  - remove site.zcml copy logic
    #  - made it relative to zope2-location
    def build_package_includes(self):
        """Create ZCML slugs in etc/package-includes
        """
        location = self.options['zope2-location']
        zcml = self.options.get('zcml')

        out = []

        if zcml:
            includes_path = os.path.join(location, 'etc', 'package-includes')
            if not os.path.exists(includes_path):
                # Zope 2.9 does not have a package-includes so we
                # create one.
                os.mkdir(includes_path)

            zcml = zcml.split()
            if '*' in zcml:
                zcml.remove('*')
            else:
                shutil.rmtree(includes_path)
                os.mkdir(includes_path)

            n = 0
            package_match = re.compile('\w+([.]\w+)*$').match
            for package in zcml:
                n += 1
                orig = package
                if ':' in package:
                    package, filename = package.split(':')
                else:
                    filename = None

                if '-' in package:
                    package, suff = package.split('-')
                    if suff not in ('configure', 'meta', 'overrides'):
                        raise ValueError('Invalid zcml', orig)
                else:
                    suff = 'configure'

                if filename is None:
                    filename = suff + '.zcml'

                if not package_match(package):
                    raise ValueError('Invalid zcml', orig)

                path = os.path.join(
                    includes_path,
                    "%3.3d-%s-%s.zcml" % (n, package, suff),
                    )
                open(path, 'w').write(
                    '<include package="%s" file="%s" />\n'
                    % (package, filename)
                    )

                out.append(path)

        return out


