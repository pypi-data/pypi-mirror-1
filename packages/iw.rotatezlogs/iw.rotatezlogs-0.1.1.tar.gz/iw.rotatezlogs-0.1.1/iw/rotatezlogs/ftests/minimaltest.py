# -*- coding: iso-8859-15 -*-

##############################################################################
#
# Copyright (c) 2006 Ingeniweb SAS
#
# This software is subject to the provisions of the GNU General Public License,
# Version 2.0 (GPL).  A copy of the GPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

"""Testing rotatezlogs

Configure a <rotatelogfile> handler in the <logger access> section of
your Zope instance, then run this script. See the main README.txt of
this packege for configuration hints.

Assuming your instance listens in http://localhost:8080, otherwise
change ZOPE_HOME_URL below.

$Id: minimaltest.py 5742 2006-06-05 19:13:43Z glenfant $
"""

import urllib2

ZOPE_HOME_URL = 'http://localhost:8080/'
SHOW_DOT_EVERY = 50

print "Refresh the view of your log directory while running this script."
print "Hit Ctrl+C to stop."
print "Will show one dot every", SHOW_DOT_EVERY, "queries."

i=0
while 1:
    fh=urllib2.urlopen(ZOPE_HOME_URL)
    dummy = fh.read()
    fh.close()
    i += 1
    if i == SHOW_DOT_EVERY:
        i = 0
        print '.',
