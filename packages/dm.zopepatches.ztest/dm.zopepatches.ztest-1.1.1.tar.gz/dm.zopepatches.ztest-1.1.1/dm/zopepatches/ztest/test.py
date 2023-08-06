#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Zope 2 test script

see zope.testing testrunner.txt

$Id: test.py,v 1.3 2009/10/16 13:40:02 dieter Exp $
"""

import os.path, sys

# Remove script directory from path:
scriptdir = os.path.realpath(os.path.dirname(sys.argv[0]))
sys.path[:] = [p for p in sys.path if os.path.realpath(p) != scriptdir]

shome = os.environ.get('SOFTWARE_HOME')
zhome = os.environ.get('ZOPE_HOME')
ihome = os.environ.get('INSTANCE_HOME')

if zhome:
    zhome = os.path.realpath(zhome)
    if shome:
        shome = os.path.realpath(shome)
    else:
        shome = os.path.join(zhome, 'lib', 'python')
elif shome:
    shome = os.path.realpath(shome)
    zhome = os.path.dirname(os.path.dirname(shome))
else:
    # No zope home, derive shome from 'Zope2'
    import Zope2
    shome = os.path.dirname(os.path.dirname(Zope2.__file__))
    zhome = os.path.dirname(os.path.dirname(shome))
    print shome, zhome

sys.path.insert(0, shome)

defaults = '--tests-pattern ^tests$ -v'.split()
defaults += ['-m',
             '!^('
             'ZConfig'
             '|'
             'BTrees'
             '|'
             'persistent'
             '|'
             'ThreadedAsync'
             '|'
             'transaction'
             '|'
             'ZEO'
             '|'
             'ZODB'
             '|'
             'ZopeUndo'
             '|'
             'zdaemon'
             '|'
             'zope[.]testing'
             '|'
             'zope[.]app'
             ')[.]']
if ihome:
    ihome = os.path.abspath(ihome)
    defaults += ['--path', os.path.join(ihome, 'lib', 'python')]
    products = os.path.join(ihome, 'Products')
    if os.path.exists(products):
        defaults += ['--package-path', products, 'Products']
else:
    defaults += ['--test-path', shome]

from zope.testing import testrunner
from zope.testing.testrunner import options

def load_config_file(option, opt, config_file, *ignored):
    config_file = os.path.abspath(config_file)
    print "Parsing %s" % config_file
    import Zope2
    Zope2.configure(config_file)

options.setup.add_option(
    '--config-file', action="callback", type="string", dest='config_file',
    callback=load_config_file,
    help="""\
Initialize Zope with the given configuration file.
""")

options.setup.add_option(
    '--no-determine-package-paths', action='store_false',
    dest='no_determine_package_paths',
    help="""disable automatic determination of package paths."""
    )

def determine_package_paths(option, opt_str, value, parser):
    from sys import modules
    from os.path import dirname
    values = parser.values
    if getattr(values, 'no_determine_package_paths', False): return
    for p in values.package:
        try: __import__(p)
        except ImportError: pass
        else:
            m = modules[p]
            if getattr(m, '__loader__', None):
                # this is something special, we probably cannot handle
                continue
            f = m.__file__
            if getattr(m, '__path__', None):
                # this is a package
                if values.package_path is None:
                    values.package_path = []
                values.package_path.append((dirname(f), p))

options.setup.add_option(
    '--determine-package-paths', action='callback',
    callback=determine_package_paths,
    help="""automatically added as last option. Will try to automatically determine package paths unless '--no-determine-package-paths' was specified.""",
    )

def filter_warnings(option, opt, *ignored):
    import warnings
    warnings.simplefilter('ignore', Warning, append=True)

options.other.add_option(
    '--nowarnings', action="callback", callback=filter_warnings,
    help="""\
Install a filter to suppress warnings emitted by code.
""")

def main():
    # try to automatically determine package paths
    sys.argv.append('--determine-package-paths')
    sys.exit(testrunner.run(defaults))
