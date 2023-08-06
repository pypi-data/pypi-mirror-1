# -*- coding: utf-8 -*-
#
# Copyright (c) InQuant GmbH
#
# This Program may be used by anyone in accordance with the terms of the 
# LGPL

__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision: 3466 $"

import os
import logging

logger = logging.getLogger("inquant.recipe.textfile")

info = logger.info
warning = logger.warning
error = logger.info

class Recipe(object):
    """
    A Recipe which creates a textfile from a template

    Parameters:

    template           ... the template file
                           default: ${buildout:template-directory}/$(name)s.in

    location           ... the output file. If not given, no file is created.

    template-directory ... the directory where the templates are located.

    Available keys:

    content      ... the content of the created template
    """

    def __init__(self, buildout, name, options):
        self.options = options
        self.buildout = buildout
        self.name = name

        buildout['buildout'].setdefault(
            'template-directory',
            os.path.join(buildout['buildout']['directory'], 'templates'))

        template_dir = options.get( "template-directory", buildout["buildout"].get( "template-directory" ) )
        options["template-directory"] = template_dir

        if not options.get('template'):
            options['template'] = "%s.in" % self.name,

        self.create_file = True
        if not options.get('location'):
            self.create_file = False

        template = os.path.join( options["template-directory"], options.get("template") )
        if not os.path.exists(template):
            raise ValueError( "Cannot access template '%(template)s'" % locals() )

        raw = file(template, "r" ).read()
        try:
            options["content"] = raw % options
        except:
            error( "Error during creation of template:" )
            raise

    def warning(self, msg ):
        logging.getLogger(self.name).warning( msg )

    def info(self, msg ):
        logging.getLogger(self.name).info( msg )

    def install(self):
        options = self.options

        if self.create_file:
            location = options.get("location")
            file( location, "w" ).write( options["content"] )
            self.info( "Created file %(location)s from template %(template)s." % options )
            return location
        else:
            return ()

    update = install

# vim: set ft=python ts=4 sw=4 expandtab :
