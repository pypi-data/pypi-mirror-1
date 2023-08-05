#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: sw=4 ts=4 fenc=utf-8
# =============================================================================
# $Id$
# =============================================================================
#             $URL$
# $LastChangedDate$
#             $Rev$
#   $LastChangedBy$
# =============================================================================
# Copyright (C) 2007 UfSoft.org - Pedro Algarvio <ufs@ufsoft.org>
#
# Please view LICENSE for additional licensing information.
# =============================================================================

import sys
try:
    import irclib
except ImportError:
    print "You need to install irclib"
    print "On Debian:"
    print "  sudo apt-get install python-irclib"
    sys.exit(1)
try:
    import pynotify
except:
    print "You need to install python-notify"
    print "On Debian:"
    print "  sudo apt-get install python-notify"
    sys.exit(1)
try:
    import pygtk
except:
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

For more information, submit bugs or if you'd like to comment about the tool
please visit:
    http://blog.ufsoft.org/index.php/category/irssi-notification/
"""

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
    url = 'http://blog.ufsoft.org/index.php/category/irssi-notification/',
    platforms = ['Anywere libnotify and python is known to run'],
    keywords = ['irssi', 'visual notification', 'notification'],
    packages = ['irssinotifier'],
    zip_safe = False,
    entry_points = """
    [console_scripts]
    irssi-notifier = irssinotifier.parser:main
    """,
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
    ]
)
