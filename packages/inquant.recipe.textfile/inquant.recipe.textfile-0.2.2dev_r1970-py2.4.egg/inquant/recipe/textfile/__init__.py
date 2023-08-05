# -*- coding: utf-8 -*-
#
# Copyright (c) InQuant GmbH
#
# This Program may be used by anyone in accordance with the terms of the 
# LGPL

__author__ = """Stefan Eletzhofer <stefan.eletzhofer@inquant.de>"""
__docformat__ = 'plaintext'
__revision__ = "$Revision: 1970 $"

import os
import logging

class Recipe(object):
    """
    A Recipe which creates a textfile from a template

    Parameters:

    template     ... the template file
                     default: ${buildout:template-directory}/$(name)s.in
    location     ... the output file
                     default: ${buildout:parts-directory}/$(name)s
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

        if not options.get('location'):
            options['location'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name,
                )

    def warning(self, msg ):
        logging.getLogger(self.name).warning( msg )

    def info(self, msg ):
        logging.getLogger(self.name).info( msg )

    def install(self):
        options = self.options

        template = os.path.join( options["template-directory"], options.get("template") )
        if not os.path.exists(template):
            raise ValueError( "Cannot access template '%(template)s'" % locals() )

        location = options.get("location")

        content = file(template, "r" ).read()
        file( location, "w" ).write( content % self.options ) 
        self.info( "Created file %(location)s from template %(template)s." % locals() )

        return location

    def update(self):
        pass

# vim: set ft=python ts=4 sw=4 expandtab :
