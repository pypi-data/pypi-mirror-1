#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id: setup.py 52 2007-10-18 16:51:59Z s0undt3ch $
# =============================================================================
#             $URL: http://irssinotifier.ufsoft.org/svn/branches/0.2.x/setup.py $
# $LastChangedDate: 2007-10-18 17:51:59 +0100 (Thu, 18 Oct 2007) $
#             $Rev: 52 $
#   $LastChangedBy: s0undt3ch $
# =============================================================================
# Copyright (C) 2007 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import os
import sys
from distutils.command.sdist import sdist

try:
    import irclib
except ImportError:
    print "You need to install irclib"
    print "On Debian:"
    print "  sudo apt-get install python-irclib"
    sys.exit(1)
try:
    import pynotify
except ImportError:
    print "You need to install python-notify"
    print "On Debian:"
    print "  sudo apt-get install python-notify"
    sys.exit(1)
try:
    import pygtk
except ImportError:
    print "You need to install Python's GTK2 support"
    print "On Debian:"
    print "  sudo apt-get install python-gtk2"
    sys.exit(1)

import irssinotifier
from setuptools import setup

LONGDESC = """
Irssi Notifier is a real-time remote visual notification of private messages,
messages sent to the user and messages where the user is addressed using
irssi's proxy module. Also notifies of friends joins, parts, quits and nick
changes, ie, it's common a user to change it's nick from 'foo' to 'foo_away'
when he's set as away.

For more information or if you'd like to comment about the tool please visit:
    http://blog.ufsoft.org/index.php/category/irssi-notification/
Or, to submit bugs/new features:
    http://irssinotifier.ufsoft.org/
"""

class MySdist(sdist):
    """Cudtom 'sdist' command to re-write the license file from what's defined
    on the package."""

    def run(self):
        license_text = irssinotifier.__license_text__
        license_file = os.path.join(os.path.dirname(__file__), 'LICENSE')
        open(license_file, 'w').write(license_text)
        sdist.run(self)

setup(
    name    = irssinotifier.__package__,
    version = irssinotifier.__version__,
    license = irssinotifier.__license__,
    author  = irssinotifier.__author__,
    maintainer = irssinotifier.__author__,
    maintainer_email = irssinotifier.__email__,
    author_email = irssinotifier.__email__,
    description = "Irssi Real Time Remote Visual Notification.",
    long_description = LONGDESC,
    url = irssinotifier.__url__,
    platforms = ['Anywere libnotify and python is known to run'],
    keywords = ['irssi', 'visual notification', 'notification'],
    packages = ['irssinotifier'],
    package_data = { 'irssinotifier': ['i18n/*/LC_MESSAGES/*.mo', 'data/*.png',
                                       'data/glade/*.glade']},
    include_package_data = True,
    zip_safe = False,
    # PyXSS tries to find SWIG on system, if not found installs the pre SWIG
    # version, should we warn the user about this?
    install_requires = ['PyXSS', 'Babel'],
    dependency_links = [
        'http://bebop.bigasterisk.com/python',
    ],
    entry_points = """
    [console_scripts]
    irssi-notifier = irssinotifier.parser:main

    [distutils.commands]
    extract = babel.messages.frontend:extract_messages
    init = babel.messages.frontend:init_catalog
    compile = babel.messages.frontend:compile_catalog
    update = babel.messages.frontend:update_catalog

    """,
    #irssi-notifier-gui = irssinotifier.ui:run_tray_app
    #""",
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: X11 Applications',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Topic :: Desktop Environment',
        'Topic :: Utilities'
    ],
    message_extractors = {
        'irssinotifier': [
            ('**.py',    'python', None),
            ('**.glade', 'glade',  None),
        ]
    },
    cmdclass = {'sdist': MySdist}
)
