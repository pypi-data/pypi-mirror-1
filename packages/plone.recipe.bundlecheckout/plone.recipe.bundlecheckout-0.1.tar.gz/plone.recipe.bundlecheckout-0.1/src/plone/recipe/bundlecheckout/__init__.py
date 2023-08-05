##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
import os, re

class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name)
        self.vcs_type = options.get('vcs-type', 'svn')

    def install(self):
        options = self.options
        location = options['location']
        if os.path.exists(location):
            # Don't do anything in offline mode
            if self.buildout['buildout'].get('offline') == 'true':
                return location
            os.chdir(location)
            if self.vcs_type == 'svn':
                os.system('svn up -q')
            if self.vcs_type == 'cvs':
                os.system('cvs -q -d %s up -P -d' % options['cvsroot'])
        else:
            if self.vcs_type == 'svn':
                assert os.system('svn co %s "%s"' % (options['url'], location)
                                 ) == 0
            if self.vcs_type == 'cvs':
                if not os.path.exists(location):
                    os.mkdir(location)
                os.chdir(location)
                os.system('cvs -d %s login' % options['cvsroot'])
                os.system('cvs -z9 -d %s co -d "%s" "%s"' %
                    (options['cvsroot'], options['name'], options['module']))

            os.chdir(location)

        return location
