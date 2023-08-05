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
import os

EGG_INFO_CONTENT = """Metadata-Version: 1.0
Name: %s
Version: 0.0
"""

class Recipe:

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        options.setdefault('additional-fake-eggs','')

    def install(self):
        zope2Location = self.buildout['zope2']['location']
        developEggDir = self.buildout['buildout']['develop-eggs-directory']
        zopeLibZopeLocation = os.path.join(zope2Location, 'lib', 'python',
                                           'zope')
        zopeLibZopeAppLocation = os.path.join(zope2Location, 'lib', 'python',
                                              'zope', 'app')
        zopeLibs = ["zope.%s" % lib for lib in os.listdir(zopeLibZopeLocation)\
                    if os.path.isdir(os.path.join(zopeLibZopeLocation, lib))]
        zopeLibs += ["zope.app.%s" % lib for lib in os.listdir(zopeLibZopeAppLocation)\
                    if os.path.isdir(os.path.join(zopeLibZopeAppLocation, lib))]
        zopeLibs += [lib for lib in self.options['additional-fake-eggs'].split('\n')]
        for zopeLib in zopeLibs:
            fakeLibEggInfoFile = os.path.join(developEggDir,
                                              '%s.egg-info' % zopeLib)
            fd = open(fakeLibEggInfoFile, 'w')
            fd.write(EGG_INFO_CONTENT % zopeLib)
            fd.close()
        return ()

    def update(self):
        return self.install()

