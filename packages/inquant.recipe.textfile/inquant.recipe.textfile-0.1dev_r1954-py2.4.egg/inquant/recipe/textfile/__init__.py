# -*- coding: utf-8 -*-
#
# Copyright (c) InQuant GmbH
#
# This Program may be used by anyone in accordance with the terms of the 
# LGPL

__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision: 1953 $"

import os
import logging

class Recipe(object):
    """
    A Recipe which creates a textfile from a template

    Parameters:

    template     ... the template file
    output       ... the output file
    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

    def warning(self, msg ):
        logging.getLogger(self.name).warning( msg )

    def info(self, msg ):
        logging.getLogger(self.name).info( msg )

    def install(self):
        options = self.options

        template = options.get("template")
        if not os.path.exists(template):
            raise ValueError( "Cannot access template '%(template)s'" % locals() )

        output = options.get("output")

        content = file(template, "r" ).read()
        file( output, "w" ).write( content % self.options ) 
        self.info( "Created file %(output)s from template %(template)s." % locals() )

        return output

    def update(self):
        pass

# vim: set ft=python ts=4 sw=4 expandtab :
