# -*- coding: utf-8 -*-
#
# Copyright (c) InQuant GmbH
#
# This Program may be used by anyone in accordance with the terms of the 
# LGPL

__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision: 1946 $"

import os
import logging
import gocept.download
import shutil

class Recipe(object):
    """
    Just a wrapper for gocept.download. This recipe does
    allow to clean out the destination path if needed.

    Parameters:

    download-directory        ... directory to store downloaded files
                                  default: ${buildout:directory}/downloads
    destination               ... directory to store extracted stuff
                                  default: ${buildout:parts-directory}
    strip-top-level-dir       ... strip the toplevel dir of the archive
                                  default: true
    clean-destination         ... clean the destination
                                  default: false
    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name
        self.package_download = gocept.download.Recipe(buildout, name, options)
        options.setdefault('clean-destination', 'false')

    def warning(self, msg ):
        logging.getLogger(self.name).warning( msg )

    def info(self, msg ):
        logging.getLogger(self.name).info( msg )

    def install(self):
        options = self.options
        loc = options.get("destination")
        self.info( "DEST=%(loc)s" % locals() )

        if loc is not None and os.path.exists( loc ):
            if options.get( "clean-destination" ) == "true":
                self.warning( "REMOVING dir %s" % loc )
                shutil.rmtree( loc )

        if not os.path.exists( loc ):
            os.mkdir( loc)

        paths = self.package_download.install()
        return paths

    def update(self):
        pass

# vim: set ft=python ts=4 sw=4 expandtab :
