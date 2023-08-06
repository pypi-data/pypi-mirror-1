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

"""Plugins for zLOG

$Id: LogHandlers.py 5746 2006-06-05 19:30:17Z glenfant $
"""

# Python standard distro
import os
import logging
from logging.handlers import RotatingFileHandler as BaseHandler
import zipfile
import gzip
try:
    import bz2
except ImportError, e:
    # Some Python/systems have no bzip2 lib/support
    # Should log something but this module is called too early for this
    bz2 = None

# Zope specific
from ZConfig.components.logger.handlers import HandlerFactory

# Reading and understanding this code requires you understand how
# zConfig.components.logger works

###
## Rotate log file handler and factory
###

class RotateFileHandler(BaseHandler):
    """A standard RotatingFileHandler with zLOG compatibility"""

    def __init__(self, path, max_bytes, backup_count, compression):
        """Built by the factory and nothing else..."""

        filename =  os.path.abspath(path)
        BaseHandler.__init__(self, filename, mode='a', maxBytes=max_bytes,
                             backupCount=backup_count)
        self.baseFilename = filename
        self.compressor = getCompressor(compression)
        return


    def doRollover(self):
        """Overrides method from logging.handlers.RotatingFileHandler"""

        self.stream.close()
        if self.backupCount > 0:
            file_pattern = self.compressor.file_pattern
            for i in range(self.backupCount - 1, 0, -1):
                sfn = file_pattern % (self.baseFilename, i)
                dfn = file_pattern % (self.baseFilename, i + 1)
                if os.path.exists(sfn):
                    if os.path.exists(dfn):
                        os.remove(dfn)
                    os.rename(sfn, dfn)
            self.compressor.compress(self.baseFilename)
        self.stream = file(self.baseFilename, "w")
        return

    def reopen(self):
        """Mandatory for the factory but useless in our case"""

        self.close()
        self.stream = open(self.baseFilename, 'a')
        return

###
## Compressors
###

class NoneCompressor(object):
    """Just rotating, no compression"""

    file_pattern = '%s.%d'

    def compress(self, filename):
        dfn = filename + '.1'
        if os.path.exists(dfn):
            os.remove(dfn)
        os.rename(filename, dfn)
        return


class ZipCompressor(object):
    """Zip compression"""

    file_pattern = '%s.%d.zip'

    def compress(self, filename):
        dfn = filename + '.1.zip'
        if os.path.exists(dfn):
            os.remove(dfn)
        zf = zipfile.ZipFile(dfn, 'w', zipfile.ZIP_DEFLATED)
        zf.write(filename, os.path.basename(filename))
        zf.close()
        os.remove(filename)
        return


class GzipCompressor(object):
    """Gzip compression"""

    file_pattern = '%s.%d.gz'

    def compress(self, filename):
        dfn = filename + '.1.gz'
        if os.path.exists(dfn):
            os.remove(dfn)
        zf = gzip.GzipFile(dfn, 'wb')
        zf.write(file(filename, 'rb').read())
        zf.close()
        os.remove(filename)
        return

if bz2:
    class Bzip2Compressor(object):
        """Bzip2 compression"""

        file_pattern = '%s.%d.bz2'

        def compress(self, filename):
            dfn = filename + '.1.bz2'
            if os.path.exists(dfn):
                os.remove(dfn)
            zf = bz2.BZ2File(dfn, 'w')
            zf.write(file(filename, 'rb').read())
            zf.close()
            os.remove(filename)
            return
else:
    Bzip2Compressor = NoneCompressor

def getCompressor(compression):
    """->compressor object"""

    # { compression mode: compressor class, ...}
    compressors = {
        'none': NoneCompressor,
        'zip': ZipCompressor,
        'gzip': GzipCompressor,
        'bzip2': Bzip2Compressor
        }

    klass = compressors.get(compression, NoneCompressor)
    return klass()

###
## Handler factory registered by component.xml
###

class RotateFileHandlerFactory(HandlerFactory):
    """Our factory referenced from the component.xml"""

    def create_loghandler(self):
        """Mandatory override"""

        return RotateFileHandler(self.section.path, self.section.max_bytes,
                                 self.section.backup_count, self.section.compression)

