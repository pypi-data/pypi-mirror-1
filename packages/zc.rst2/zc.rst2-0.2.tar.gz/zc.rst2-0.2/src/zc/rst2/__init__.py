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
import sys, pkg_resources

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

import docutils.core, docutils.parsers.rst.directives

description = ('Generates various from standalone reStructuredText sources.  '
               + docutils.core.default_description)


def load_directives():
    for entry_point in pkg_resources.iter_entry_points('rst.directive'):
        docutils.parsers.rst.directives.register_directive(
            entry_point.name, entry_point.load())

def main():
    if len(sys.argv) < 2:
        writer = 'html'
    else:
        writer = sys.argv.pop(1)

    load_directives()
    docutils.core.publish_cmdline(writer_name=writer, description=description)
