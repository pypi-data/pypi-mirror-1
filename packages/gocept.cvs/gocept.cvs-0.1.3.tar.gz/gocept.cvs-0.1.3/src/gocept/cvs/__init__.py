##############################################################################
#
# Copyright (c) 2008 gocept gmbh & co. kg and Contributors.
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
import os.path

class Recipe:
    """Recipe that checks out cvs modules

    Configuration options:

        cvsroot
        destination
        modules

    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name
        self.offline = buildout['buildout'].get('offline', 'false') == 'true'

        if not options.get('destination'):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name,
                )
        else:
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'],
                options.get('destination'))
            
    def update(self):
        destination = self.options.get('location')
        if self.offline:
            return destination

        cvsroot = self.options.get('cvsroot')
        modules = self.options.get('modules')
        modules_tags_dest = get_modules_tags_dest(modules)
        for module, tag, dest in modules_tags_dest:
            if os.path.isdir(destination+dest):
                single_update(destination, dest, tag)
            else:
                single_checkout(module, destination, dest, tag, cvsroot)
        return destination

    def install(self):
        destination = self.options.get('location')
        if self.offline:
            raise Exception("Cannot install %s in offline-mode!" % destination)
        cvsroot = self.options.get('cvsroot')
        modules = self.options.get('modules')
        if not os.path.isdir(destination):
            os.mkdir(destination)
        modules_tags_dest = get_modules_tags_dest(modules)
        for module, tag, dest in modules_tags_dest:
            single_checkout(module, destination, dest, tag, cvsroot)
        return destination

def single_checkout(path, location, dest, tag, cvsroot):
    cmd = ['cd %s &&' % location, 'CVSROOT=%s' % cvsroot, 'cvs', 'co']
    if tag:
        cmd.append('-r %s' % tag)
    cmd += ['-d %s' % dest, path] 
    call(cmd)

def single_update(location, dest, tag):
    cmd = ['cd %s &&' % location, 'cvs', 'up', '-d', '-P']
    if tag:
        cmd.append('-r %s' % tag)
    cmd.append(dest)
    call(cmd)

def get_modules_tags_dest(modules):
    for module in modules.splitlines():
        module = module.strip()
        mtd = module.split(';')
        if len(mtd) != 3:
            raise Exception("Parse error in modules parameter: %s" % module)
        yield tuple(mtd)

def call(commands):
    cmd = ' '.join(commands)
    os.system(' '.join(commands))
