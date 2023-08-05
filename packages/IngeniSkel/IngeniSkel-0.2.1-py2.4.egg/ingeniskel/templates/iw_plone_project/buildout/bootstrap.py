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
"""Bootstrap a buildout-based project

Simply run this script in a directory containing a buildout.cfg.
The script accepts buildout command-line options, so you can
use the -c option to specify an alternate configuration file.

$Id$
"""

import os, shutil, sys, tempfile, urllib2

tmpeggs = tempfile.mkdtemp()

try:
    import pkg_resources
except ImportError:
    import glob
    setuptools = glob.glob(os.path.join(os.path.abspath(os.curdir), 'eggs', 'setuptools-*'))
    setuptools.sort()
    setuptools.reverse()
    if setuptools:
        print 'Using setuptools from %s' % setuptools[0]
        sys.path.insert(0, setuptools[0])

try:
    import zc.buildout
except ImportError:
    import glob
    buildout = glob.glob(os.path.join(os.path.abspath(os.curdir), 'eggs', 'zc.buildout-*'))
    buildout.sort()
    buildout.reverse()
    if buildout:
        print 'Using zc.buildout from %s' % buildout[0]
        sys.path.insert(0, buildout[0])

try:
    import pkg_resources
except ImportError:
    ez = {}
    exec urllib2.urlopen('http://peak.telecommunity.com/dist/ez_setup.py'
                         ).read() in ez
    ez['use_setuptools'](to_dir=tmpeggs, download_delay=0)
    import pkg_resources

cmd = 'from setuptools.command.easy_install import main; main()'
if sys.platform == 'win32':
    cmd = '"%s"' % cmd # work around spawn lamosity on windows

ws = pkg_resources.working_set
ws.add_entry(tmpeggs)

try:
    ws.require('zc.buildout')
    from zc.buildout.buildout import main 
    main(sys.argv[1:] + ['bootstrap'])
finally:
    try:
        import shutils
        shutils.rmtree(tmpeggs)
    except ImportError:
        # not doing this on win32
        pass

