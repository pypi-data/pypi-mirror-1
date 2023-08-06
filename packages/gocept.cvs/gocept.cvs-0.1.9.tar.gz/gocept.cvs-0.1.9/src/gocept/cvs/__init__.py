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
import subprocess
import re

LOCALCHANGES_REGEXP = re.compile('[\?|M|A|R|C].\w+')


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
        self.newest = buildout['buildout'].get('newest', 'false') == 'true'

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
            if os.path.isdir(os.path.join(destination, dest)):
                if self.newest:
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


def uninstall(name, options):
    """

    Its only job is to raise an exception when there are
    changes in a subversion tree that a user might not want to
    lose.  This function does *not* delete or otherwise touch
    any files.

    The location of the path is passed as options['location'].
    """
    location = options.get('location', os.path.join('.', 'parts', name))
    modules = options.get('modules')
    modules_tags_dest = get_modules_tags_dest(modules)
    bad_modules = []
    for module, tag, dest in modules_tags_dest:
        if not os.path.isdir(os.path.join(location,dest)):
            continue

        output, status = check_for_changes(location, dest, tag)
        if LOCALCHANGES_REGEXP.match(output):
            raise ValueError(
                "Local changes are made in %s. Revert them"
                " first to update/uninstall using buildout."
                " \n--\n%s" %(dest, output))


def single_checkout(path, location, dest, tag, cvsroot):
    dest_dir, dest_name = os.path.split(dest)
    cmd = ['cvs', 'co']
    if tag and tag != 'HEAD':
        cmd.append('-r%s' % tag)
    cmd += ['-d%s' % dest_name, path]
    os.putenv('CVSROOT', cvsroot)
    os.chdir(os.path.join(location, dest_dir))
    call(cmd)


def single_update(location, dest, tag):
    cmd = ['cvs', '-q', 'up', '-d', '-P']
    if tag and tag != 'HEAD':
        cmd.append('-r%s' % tag)
    elif tag == 'HEAD':
        cmd.append('-A')
    cmd.append(dest)
    os.chdir(location)
    return call(cmd)


def check_for_changes(location, dest, tag):
    """Checks if there are changes in the local checkout."""
    cmd = ['cvs', '-q', '-n', 'up']
    cmd.append(dest)
    os.chdir(location)
    return call(cmd, 1)


def get_modules_tags_dest(modules):
    for module in modules.splitlines():
        module = module.strip()
        mtd = module.split(';')
        if len(mtd) != 3:
            raise Exception("Parse error in modules parameter: %s" % module)
        yield tuple(mtd)


def call(commandlist, return_stdout=0):
    if return_stdout:
        popen = subprocess.Popen(commandlist, stdout=subprocess.PIPE)
    else:
        popen = subprocess.Popen(commandlist)
    return popen.communicate()
