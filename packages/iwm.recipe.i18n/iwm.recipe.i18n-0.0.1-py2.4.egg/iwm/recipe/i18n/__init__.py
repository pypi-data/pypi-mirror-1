##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""A few built-in recipes

$Id$
"""

import os, sys
import pkg_resources
import zc.buildout.easy_install
import zc.recipe.egg


class I18n:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        options['script'] = os.path.join(buildout['buildout']['bin-directory'],
                                         self.name,
                                         )
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'], name)
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options
        dest = []
        eggs, ws = self.egg.working_set(('zope.testing', ))

        bin_dir = self.buildout['buildout']['bin-directory']
        
        wd = options['location']
        dest.append(wd)

        # i18nextract
        initi18nextract = initi18nextract_template
        i18nextract_path = os.path.join(bin_dir, 'i18nextract')
        dest.extend(zc.buildout.easy_install.scripts(
            [('i18nextract', 'i18nextract', 'main')],
            ws, options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths=self.egg.extra_paths,
            initialization = initi18nextract,
            ))

        # i18nmergeall
        initi18nmergeall = initi18nmergeall_template
        dest.extend(zc.buildout.easy_install.scripts(
            [('i18nmergeall', 'iwm.recipe.i18n.ctl', 'main_i18nmergeall')],
            ws, options['executable'],
            self.buildout['buildout']['bin-directory'],
            extra_paths=self.egg.extra_paths,
            initialization = initi18nmergeall,
            ))

        return dest

    update = install



initi18nextract_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""

initi18nmergeall_template = """import os
sys.argv[0] = os.path.abspath(sys.argv[0])
"""
