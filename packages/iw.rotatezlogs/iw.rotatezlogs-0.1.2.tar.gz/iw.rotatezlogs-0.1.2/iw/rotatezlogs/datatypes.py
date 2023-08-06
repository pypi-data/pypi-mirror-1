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

"""keys values control for ZConfig

$Id: datatypes.py 5745 2006-06-05 19:22:53Z glenfant $
"""

def compression_mode(value):
    """Validates the compression key from config"""

    possible_values = ('none', 'zip', 'gzip', 'bzip2')
    value = str(value).lower()
    if value not in possible_values:
        raise ValueError("Invalid compression mode %s" % value)
    return value
