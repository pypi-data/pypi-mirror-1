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
import sys

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

import docutils.core

description = ('Generates various from standalone reStructuredText sources.  '
               + docutils.core.default_description)



def main():
    if len(sys.argv) < 2:
        writer = 'html'
    else:
        writer = sys.argv.pop(1)
    
    docutils.core.publish_cmdline(writer_name=writer, description=description)
